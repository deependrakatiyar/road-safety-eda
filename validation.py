"""Padhai AI — Input Validation & Safety Engine."""
import re
from typing import Optional

CLASS_SUBJECTS: dict = {
    "Class 6":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 7":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 8":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 9":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit",
                 "Computer Science"],
    "Class 10": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit",
                 "Computer Science"],
    "Class 11": ["Hindi", "English", "Physics", "Chemistry", "Mathematics", "Biology",
                 "History", "Geography", "Political Science", "Economics",
                 "Business Studies", "Accountancy", "Computer Science"],
    "Class 12": ["Hindi", "English", "Physics", "Chemistry", "Mathematics", "Biology",
                 "History", "Geography", "Political Science", "Economics",
                 "Business Studies", "Accountancy", "Computer Science"],
}

CLASSES: list = list(CLASS_SUBJECTS.keys())
SUBJECTS: dict = CLASS_SUBJECTS

# Subject → broad subdomain labels used for cross-contamination detection.
# If AI response on Subject X contains 2+ signals from another subject, flag it.
_CROSS_SIGNALS: dict = {
    "Mathematics":      ["democracy", "parliament act", "photosynthesis",
                         "cell division", "1857 revolt", "poem recital"],
    "Science":          ["democracy", "parliament act", "election commission",
                         "essay writing", "poem analysis"],
    "Physics":          ["democracy", "parliament act", "photosynthesis",
                         "cell division", "poem analysis"],
    "Chemistry":        ["democracy", "parliament act", "photosynthesis",
                         "cell division", "poem analysis"],
    "Biology":          ["quadratic equation", "trigonometry formula",
                         "democracy act", "parliament session"],
    "History":          ["quadratic equation", "chemical formula",
                         "cell membrane", "trigonometry"],
    "Geography":        ["quadratic equation", "chemical formula",
                         "cell membrane", "trigonometry"],
    "Political Science":["quadratic equation", "chemical formula",
                         "photosynthesis", "trigonometry"],
    "Economics":        ["quadratic equation", "cell membrane",
                         "trigonometry formula", "poem recital"],
    "Hindi":            ["newton's law", "quadratic equation",
                         "chemical formula", "cell membrane"],
    "English":          ["newton's law", "quadratic equation",
                         "chemical formula", "photosynthesis"],
    "Computer Science": ["photosynthesis", "mughal empire",
                         "cell division", "poem recital"],
    "Sanskrit":         ["quadratic equation", "chemical formula",
                         "cell division", "photosynthesis"],
    "Social Science":   ["quadratic equation", "trigonometry formula",
                         "chemical formula", "cell membrane"],
    "Business Studies": ["photosynthesis", "cell division",
                         "trigonometry", "quadratic equation"],
    "Accountancy":      ["photosynthesis", "cell division",
                         "mughal empire", "trigonometry"],
}

_UNSAFE = re.compile(r'[<>{};|`$\\]')


def validate_input(subject: str, topic: str, cls: str = "",
                   max_len: int = 200) -> tuple:
    """
    Returns (True, None) if valid, (False, error_message) if invalid.
    Checks: class-subject alignment, topic length, no injection chars.
    """
    if cls and cls in CLASS_SUBJECTS:
        if subject not in CLASS_SUBJECTS[cls]:
            return False, f"'{subject}' is not in the {cls} syllabus."

    t = topic.strip()
    if not t:
        return False, "Topic / Chapter ka naam likhna zaruri hai."
    if len(t) < 2:
        return False, "Topic naam bahut chhota hai — thoda aur specific likhein."
    if len(t) > max_len:
        return False, f"Topic bahut lamba hai (max {max_len} characters)."
    if _UNSAFE.search(t):
        return False, "Topic mein invalid characters hain. Sirf text likhein."

    return True, None


def check_response_contamination(subject: str, response: str) -> tuple:
    """
    Soft check for cross-subject content in an AI response.
    Returns (True, None) if clean.
    Returns (False, warning_msg) only if 2+ cross-domain signals found,
    to minimise false positives.
    """
    signals = _CROSS_SIGNALS.get(subject)
    if not signals:
        return True, None

    lower = response.lower()
    hits = [kw for kw in signals if kw in lower]
    if len(hits) >= 2:
        return False, "Response mein off-topic content ho sakta hai. NCERT textbook se verify karein."
    return True, None
