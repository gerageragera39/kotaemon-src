from __future__ import annotations

from pathlib import Path
from typing import Any

import gradio as gr
import pandas as pd
from ktem.app import BasePage
from ktem.evaluation import find_default_dataset_path, load_eval_dataset, run_evaluation


CARD_STYLE = """
<style>
.eval-hero {
  border-radius: 18px;
  padding: 22px 26px;
  margin-bottom: 14px;
  background: linear-gradient(135deg, rgba(99,102,241,.14), rgba(16,185,129,.12));
  border: 1px solid rgba(148,163,184,.25);
}
.eval-hero h1 { margin: 0 0 8px; font-size: 28px; }
.eval-hero p { margin: 0; color: var(--body-text-color-subdued); font-size: 15px; }
.eval-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 10px 0 16px;
}
.eval-card {
  border-radius: 14px;
  border: 1px solid rgba(148,163,184,.28);
  padding: 14px 16px;
  background: rgba(255,255,255,.04);
}
.eval-card .label { color: var(--body-text-color-subdued); font-size: 12px; }
.eval-card .value { font-size: 24px; font-weight: 700; margin-top: 4px; }
</style>
"""


class EvaluationPage(BasePage):
    """UI for evaluating the Kotaemon RAG chatbot on a curated dataset."""

    def __init__(self, app):
        super().__init__(app)
        self.default_dataset_path = str(find_default_dataset_path() or "rag_eval_dataset.json")
        self.on_building_ui()

    def on_building_ui(self):
        gr.HTML(
            CARD_STYLE
            + """
            <div class="eval-hero">
              <h1>RAG Evaluation</h1>
              <p>
                Runs questions from rag_eval_dataset through the current Kotaemon RAG,
                collects retrieved contexts, and scores quality with local Kotaemon
                evaluator models.
              </p>
            </div>
            """
        )

        with gr.Row(equal_height=True):
            with gr.Column(scale=3):
                self.dataset_path = gr.Textbox(
                    label="Dataset path",
                    value=self.default_dataset_path,
                    placeholder="rag_eval_dataset.json",
                    info="JSON/JSONL with question, ground_truth/reference, and source_file fields.",
                )
            with gr.Column(scale=1, min_width=180):
                self.reload_btn = gr.Button("Reload dataset", variant="secondary")

        self.dataset_status = gr.Markdown()
        with gr.Row():
            self.question_limit = gr.Slider(
                minimum=1,
                maximum=1,
                value=1,
                step=1,
                label="Number of questions to ask the chatbot",
                info="Run a quick smoke test or the full dataset.",
            )
            self.enable_ragas = gr.Checkbox(
                label="Compute RAGAS metrics",
                value=True,
                info="Uses local LLM/embeddings from Kotaemon settings, without an OpenAI API key.",
            )

        self.dataset_preview = gr.DataFrame(
            label="Dataset preview",
            interactive=False,
            wrap=True,
        )

        with gr.Row():
            self.run_btn = gr.Button("Run evaluation", variant="primary", size="lg")
            self.clear_btn = gr.Button("Clear results", variant="secondary")

        self.run_status = gr.Markdown()
        self.summary_html = gr.HTML()

        with gr.Tabs():
            with gr.Tab("RAGAS scores"):
                self.ragas_scores = gr.DataFrame(
                    label="Per-question RAGAS metrics",
                    interactive=False,
                    wrap=True,
                )
            with gr.Tab("Answers & contexts"):
                self.samples_table = gr.DataFrame(
                    label="Generated answers, retrieved chunks and errors",
                    interactive=False,
                    wrap=True,
                )
            with gr.Tab("Warnings"):
                self.warnings_box = gr.Textbox(
                    label="Warnings / errors",
                    lines=8,
                    interactive=False,
                )

    @staticmethod
    def _empty_outputs(status: str):
        return (
            status,
            gr.update(maximum=1, value=1),
            pd.DataFrame(),
        )

    def load_dataset_preview(self, dataset_path: str):
        try:
            resolved = Path(dataset_path).expanduser().resolve()
            samples = load_eval_dataset(resolved)
            preview = pd.DataFrame(samples).head(10)
            count = len(samples)
            return (
                f"✅ Loaded **{count}** questions from `{resolved}`.",
                gr.update(maximum=max(count, 1), value=min(5, max(count, 1))),
                preview,
            )
        except Exception as exc:
            return self._empty_outputs(f"❌ Dataset load failed: `{exc}`")

    @staticmethod
    def _summary_cards(summary: dict[str, Any]) -> str:
        if not summary:
            return ""

        preferred = [
            "samples_total",
            "samples_ok",
            "samples_failed",
            "avg_latency_sec",
            "context_precision",
            "context_recall",
            "faithfulness",
            "answer_relevancy",
            "factual_correctness",
            "answer_correctness",
            "ragas_local_score",
            "semantic_similarity",
            "non_llm_string_similarity",
            "answer_keyword_recall",
            "context_keyword_recall",
        ]
        keys = [key for key in preferred if key in summary]
        keys += [key for key in summary if key not in keys]

        def label(key: str) -> str:
            return key.replace("_", " ").title()

        cards = "".join(
            f'<div class="eval-card"><div class="label">{label(key)}</div>'
            f'<div class="value">{summary[key]}</div></div>'
            for key in keys
        )
        return f'<div class="eval-summary-grid">{cards}</div>'

    @staticmethod
    def _display_samples(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        columns = [
            "id",
            "status",
            "source_file",
            "indexed_source",
            "question",
            "reference",
            "answer",
            "context_count",
            "top_score",
            "top_context_preview",
            "latency_sec",
            "error",
        ]
        visible_columns = [col for col in columns if col in df.columns]
        # Do not show completely empty technical columns; they look broken in Gradio.
        visible_columns = [
            col
            for col in visible_columns
            if col != "error" or df[col].fillna("").astype(str).str.len().sum() > 0
        ]
        return df[visible_columns].where(pd.notna(df[visible_columns]), "")

    @staticmethod
    def _display_scores(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        # Gradio renders NaN as "undefined"; use an empty cell for unavailable
        # judge-only metrics and keep fallback/local metric values visible.
        df = df.copy()
        for column in df.columns:
            if column not in {"id", "source_file"}:
                numeric_values = pd.to_numeric(df[column], errors="coerce")
                if numeric_values.notna().any():
                    df[column] = numeric_values.round(4)
        return df.astype(object).where(pd.notna(df), "")

    def run_evaluation_ui(
        self,
        dataset_path: str,
        question_limit: float,
        enable_ragas: bool,
        settings: dict,
        user_id: Any,
        progress=gr.Progress(track_tqdm=False),
    ):
        try:
            total = max(1, int(question_limit))

            def on_progress(done: int, all_items: int, desc: str):
                progress((done, all_items), desc=desc)

            progress((0, total), desc="Starting evaluation")
            result = run_evaluation(
                app=self._app,
                settings=settings,
                user_id=user_id,
                dataset_path=dataset_path,
                question_limit=total,
                run_ragas_metrics=enable_ragas,
                progress=on_progress,
            )
            progress((total, total), desc="Done")

            status_icon = "✅" if result.summary.get("samples_failed", 0) == 0 else "⚠️"
            warnings_text = "\n".join(result.warnings)
            if enable_ragas and result.ragas_scores.empty:
                warnings_text = (warnings_text + "\n" if warnings_text else "") + (
                    "RAGAS table is empty. Check that ragas is installed and a local "
                    "LangChain-compatible LLM/embedding model is configured in Kotaemon."
                )

            return (
                f"{status_icon} Evaluation finished: "
                f"{result.summary.get('samples_ok', 0)}/{result.summary.get('samples_total', 0)} samples OK.",
                self._summary_cards(result.summary),
                self._display_scores(result.ragas_scores),
                self._display_samples(result.samples),
                warnings_text,
            )
        except Exception as exc:
            return (
                f"❌ Evaluation failed: `{exc}`",
                "",
                pd.DataFrame(),
                pd.DataFrame(),
                str(exc),
            )

    @staticmethod
    def clear_results():
        return "", "", pd.DataFrame(), pd.DataFrame(), ""

    def on_register_events(self):
        self.reload_btn.click(
            self.load_dataset_preview,
            inputs=[self.dataset_path],
            outputs=[self.dataset_status, self.question_limit, self.dataset_preview],
            show_progress="hidden",
        )
        self.run_btn.click(
            self.run_evaluation_ui,
            inputs=[
                self.dataset_path,
                self.question_limit,
                self.enable_ragas,
                self._app.settings_state,
                self._app.user_id,
            ],
            outputs=[
                self.run_status,
                self.summary_html,
                self.ragas_scores,
                self.samples_table,
                self.warnings_box,
            ],
        )
        self.clear_btn.click(
            self.clear_results,
            inputs=[],
            outputs=[
                self.run_status,
                self.summary_html,
                self.ragas_scores,
                self.samples_table,
                self.warnings_box,
            ],
            show_progress="hidden",
        )

    def _on_app_created(self):
        self._app.app.load(
            self.load_dataset_preview,
            inputs=[self.dataset_path],
            outputs=[self.dataset_status, self.question_limit, self.dataset_preview],
            show_progress="hidden",
        )
