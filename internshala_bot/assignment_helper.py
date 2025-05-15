"""
This file is a part of Internshala-bot Package. 
Github - https://github.com/Eviltr0N/internshala-bot
Written by - Mayank Lodhi
"""

from typing import Dict, Any, Union, Callable, List

def get_form_handlers(page) -> Dict[str, Dict[str, Any]]:
    """
    Builds a mapping of question-label text → handler information.

    ┌─────────────┐     handler["type"] can be one of
    │  questions  │     ──────────────────────────────────────
    │  ─────────  │     • "radio"   → handler["select"](option_text)
    │  "label"    │     • "text"    → handler["fill"](text)
    │  [options]  │     • "numeric" → handler["fill"](int|float)
    └─────────────┘
    Written by Claude.ai and ChatGPT (being honest)
    """
    questions_map: Dict[str, Dict[str, Any]] = {}

    # All additional questions are wrapped in this class
    questions = page.query_selector_all('.form-group.additional_question')

    for q_index, container in enumerate(questions):
        # Grab the visible label
        question_text = container.eval_on_selector(
            '.assessment_question label',
            'el => el.textContent.trim()'
        )

        # 1️⃣  Radio-button groups ------------------------------------------------
        radio_group = container.query_selector('.radio_group')
        if radio_group:
            radio_elements = radio_group.query_selector_all('.radio')

            radio_options = [
                {
                    'text': el.eval_on_selector('label', 'l => l.textContent.trim()'),
                    'index': idx
                }
                for idx, el in enumerate(radio_elements)
            ]

            def select_option(option_text: str,
                              q_idx: int = q_index,
                              opts=radio_options) -> None:
                # Find the matching option; fall back to first
                target_index = next(
                    (opt['index'] for opt in opts
                     if opt['text'].strip() == option_text.strip()),
                    0
                )
                page.locator('.form-group.additional_question').nth(q_idx) \
                    .locator('.radio').nth(target_index) \
                    .locator('label').click()

            questions_map[question_text] = {
                'type': 'radio',
                'options': [opt['text'] for opt in radio_options],
                'select': select_option
            }
            continue  # already handled, move to next question

        # 2️⃣  Free-text <textarea> ---------------------------------------------
        text_area = container.query_selector('textarea')
        if text_area:
            def fill_text(text: str, q_idx: int = q_index) -> None:
                page.locator('.form-group.additional_question').nth(q_idx) \
                    .locator('textarea').fill(text)

            questions_map[question_text] = {
                'type': 'text',
                'fill': fill_text
            }
            continue

        # 3️⃣  Numeric <input type="number"> -------------------------------------
        numeric_input = container.query_selector('input[type="number"]')
        if numeric_input:
            def fill_numeric(value: Union[int, float, str],
                             q_idx: int = q_index) -> None:
                # Coerce to string because Playwright fill() expects str
                page.locator('.form-group.additional_question').nth(q_idx) \
                    .locator('input[type="number"]').fill(str(value))

            questions_map[question_text] = {
                'type': 'numeric',
                'fill': fill_numeric
            }
            continue

        # 4️⃣  Unknown question type ---------------------------------------------
        print(f"Warning: Unrecognised question type for '{question_text}'")

    return questions_map

