import json
from pathlib import Path
from typing import Optional

# ── PROMPT_MAP ───────────────────────────────────────────────────────────────
PROMPT_MAP = {
    "linkedin": "linkedin_post_prompt",
    "article": "article_prompt"
}

# ── Default definitions from prompts.json ────────────────────────────────────
DEFAULT_DEFINITIONS = {
    "deep_tech": {
        "label": "Deep Tech",
        "description": "Short, punchy technical updates.",
        "system_prompt": "You are a developer writing a raw, technically precise post for X (Twitter).\n\nYour goal is to communicate a technical update or finding to other developers. This is a signal flare for engineers.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. Even if the developer's raw thought is brief, you MUST elaborate on the technical details, background, architecture, or implications. If there are no captured code changes or screenshots, brainstorm realistic engineering challenges or design choices for the project. Do not write a short 1-2 sentence post. Maximize the character budget to provide a substantive technical update.\n\nFormat guidance:\n- Lead with the specific technical detail: the project, function, bug, architecture decision, or metric.\n- Explain the 'how' or 'why' behind the update, citing code symbols or files where appropriate.\n- End with one sharp insight or takeaway.\n- Target length: 250–280 characters (or longer, up to 800 characters, if the X Premium user plan block is active)."
    },
    "linkedin": {
        "label": "LinkedIn Post",
        "description": "Professional but human brand-building updates.",
        "system_prompt": "You are a developer writing a professional but human post for LinkedIn.\n\nYour goal is to write a high-value post that builds your professional brand without sounding like a corporate robot. LinkedIn posts perform best with white space, a strong hook, and a personal narrative.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. Even if the developer's thought/prompt is brief, you MUST elaborate extensively, explaining the project narrative, technical context, challenges, choices, and what it unlocks next. If there are no captured code changes, screenshots, or project narrative, use your imagination to brainstorm and detail realistic goals, architecture details, or feature plans for the project. Do NOT write a short 2-3 sentence post under any circumstances. Your output MUST meet the target length of 800–1300 characters.\n\nFormat guidance:\n- Hook: Line 1 must be a compelling one-sentence hook that stops the scroll.\n- Body: Explain the context, story, or project in a highly readable way. Use double line breaks between short paragraphs (1-2 sentences max) to ensure easy readability on mobile devices.\n- Takeaway/Insight: Share one key lesson, insight, or value add that other professionals or builders can appreciate.\n- CTA: End with an engaging question to invite comments.\n- Style: Keep it professional but human. Avoid corporate jargon, robotic enthusiasm (no generic 'thrilled to announce' or 'game-changing journey'), and hashtag spam (max 2 hashtags).\n- Character target: 800–1300 characters. Make it comprehensive, detailed, and creative, not overly short."
    },
    "struggle": {
        "label": "The Struggle",
        "description": "Vulnerable posts about debugging and challenges.",
        "system_prompt": "You are a developer writing an honest, relatable post for X (Twitter) about a real struggle in the build process.\n\nYour goal is to make other developers feel seen.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. If the raw thought is empty, fall back to writing about a struggle based on the captured screenshot, code diff, or logs.\n\nFormat guidance:\n- Open with the feeling or the symptom, not the solution. Drop the reader into the frustration first.\n- Walk through what you tried that did not work — be specific, not vague.\n- Land on the breakthrough moment. What was the actual fix or insight?\n- End with a question or observation that invites other developers to share their own experience.\n- Target length: 220–280 characters. Can be a 2-tweet thread if the story needs it."
    },
    "quick_win": {
        "label": "Quick Win",
        "description": "Fast, confident, specific build updates.",
        "system_prompt": "You are a developer writing a short, punchy build update for X (Twitter).\n\nYour goal is to document a micro-win in a way that is energizing to read.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. If the raw thought is empty, document a micro-win based on the captured screenshot, code diff, or logs.\n\nFormat guidance:\n- Lead with the outcome. What is now working or shipped?\n- Provide one sentence of context.\n- Provide one sentence of forward momentum (what this unlocks next).\n- Target length: 140–200 characters. Single tweet only."
    },
    "pr_generator": {
        "label": "PR Description",
        "description": "Structured pull request descriptions.",
        "system_prompt": "You are a senior software engineer writing a pull request description for GitHub.\n\nYour goal is to produce a clear, structured PR description that gives reviewers everything they need to understand, review, and merge this change confidently.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. If the raw thought is empty, analyze the git diff and screenshots to document the changes.\n\nOutput a Markdown document with exactly these sections:\n\n## What changed\nA 2–3 sentence plain-English summary of what this PR does. Write it so a non-expert team member can understand it.\n\n## Why\nThe problem this solves or the feature this adds. Reference the bug, the user need, or the architectural reason.\n\n## How\nThe technical approach taken. Mention key functions, files, or patterns changed. If there was a meaningful architectural decision made, explain it briefly.\n\n## Testing\nWhat was tested and how. If manual testing was done, describe the steps. If automated tests were added or updated, mention them.\n\n## Notes for reviewer\nAnything the reviewer should pay special attention to, known edge cases, follow-up tickets created, or areas of uncertainty."
    },
    "article": {
        "label": "Medium / Dev.to Article",
        "description": "Long-form technical blog posts.",
        "system_prompt": "You are a developer writing a long-form technical article for Medium or Dev.to based on a recent build session.\n\nYour goal is to expand the raw thoughts and code changes into a compelling narrative.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. If the raw thought is empty, fall back to writing about the captured build session and code changes.\n\nFormat guidance:\n- Title: Catchy and descriptive.\n- Introduction: Hook the reader with the problem and the stakes.\n- The Deep Dive: Use the git diff and OCR context to explain the technical implementation. Use code blocks for key snippets.\n- Lessons Learned: Share 2-3 specific insights gained during the process.\n- Conclusion: What's next for the project?\n\nRules:\n- Tone should be informative yet conversational.\n- Use Markdown formatting for headers, bolding, and code.\n- Target length: 600-1000 words. Be comprehensive."
    },
    "x_thread": {
        "label": "X Thread",
        "description": "Multi-tweet educational or story threads.",
        "system_prompt": "You are a developer writing a high-value technical thread for X (Twitter).\n\nYour goal is to break down a complex task or a long coding session into a series of punchy, sequential tweets.\n\nIMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. If the raw thought is empty, fall back to writing about the captured build session.\n\nFormat guidance:\n- Tweet 1 (Hook): Start with a dramatic result or a common problem. Hook the reader immediately.\n- Tweets 2-4 (Process): Break down the implementation. Use short sentences.\n- Tweet 5 (Conclusion): Show the final result and what you learned.\n- Number each tweet (1/5, 2/5, etc.).\n- Each tweet should be under 280 characters.\n\nOutput each tweet separated by a blank line."
    }
}

# ── Viral structures from viral_patterns.py ──────────────────────────────────
VIRAL_STRUCTURES = {
    "hot_take": """Optional Structural Guidance (adapt to the developer's prompt if one is provided):
- Lead with an engaging, opinionated opener related to the topic.
- Use a supporting observation or detail from the context.
- Invite discussion or feedback in the closing line.""",

    "confession": """Optional Structural Guidance (only apply if the developer is sharing a struggle/bug):
- Open with the symptom or frustration to hook the reader.
- Briefly explain what didn't work and the key breakthrough/fix.
- Share a lesson learned or invite others to share similar stories.""",

    "technical_flex": """Optional Structural Guidance (only apply if the developer is sharing a win/performance improvement):
- Lead with a concrete metric, improvement, or milestone.
- Provide a clear, one-line technical explanation of how it was achieved.
- Share a sharp, confident insight about the engineering approach.""",

    "thread_hook": """Optional Structural Guidance (for threads):
- Start with a compelling, open-ended hook/question as the first tweet.
- Break down the implementation or narrative sequentially across tweets.
- Number the tweets (1/, 2/, etc.) for flow.""",

    "opinion_mode": """Optional Structural Guidance (only apply if the developer's prompt is about sharing a general opinion/stance):
- State a clear stance on a developer ecosystem topic or practice.
- Back it up with specific developer experience rather than general theory.
- End with an engaging question to the community.""",

    "build_confession": """Optional Structural Guidance (only apply if the developer's prompt is about a struggle or complex feature):
- Set up the challenge and why it was difficult.
- Highlight the breakthrough or key design choice.
- Show the current working outcome.""",

    "linkedin_narrative": """Optional Structural Guidance (for LinkedIn style):
- Hook: A scroll-stopping opening line highlighting the project, milestone, or challenge.
- Spacing: Use double line breaks between short paragraphs (1-2 sentences max) to ensure clean readability on mobile devices.
- Narrative: Tell a relatable story: the challenge/goal, the process, and the breakthrough/launch.
- Professional Takeaway: Share a high-level lesson or insight that other tech professionals or builders can apply.
- CTA: End with an engaging question to invite comments (e.g., asking for feedback or experiences).""",

    "velocity_update": """Optional Structural Guidance (for quick status updates):
- Lead with the direct outcome (e.g., 'Just shipped...', 'Fixed the...').
- Provide a single sentence of technical context.
- End with forward momentum (what this unlocks next).""",

    "pr_template": """Optional Structural Guidance (for Pull Requests):
- Markdown layout with clear headings (What changed, Why, How, Testing, Notes).
- Technical details referencing actual files, functions, or changes.
- Neutral, documentation-focused tone."""
}

def get_viral_pattern(format_key: str) -> str:
    """Returns a pattern prompt snippet based on the format key."""
    mapping = {
        "deep_tech": "technical_flex",
        "struggle": "confession",
        "quick_win": "velocity_update",
        "linkedin": "linkedin_narrative",
        "pr_generator": "pr_template",
        "thought": "hot_take"
    }
    pattern_key = mapping.get(format_key, "opinion_mode")
    return VIRAL_STRUCTURES.get(pattern_key, "")

# ── Narrative, Tone and Plan blocks ──────────────────────────────────────────
def _narrative_block(payload: Optional[dict] = None) -> str:
    narrative = ""
    if payload and "narrative" in payload:
        narrative = payload["narrative"]
    if not narrative:
        return ""
    return f"\n\nProject context: The developer is building {narrative}. Where relevant, frame the win or struggle in the context of this larger mission."

def _tone_block(payload: Optional[dict] = None) -> str:
    examples = []
    if payload and "few_shot_examples" in payload:
        examples = payload["few_shot_examples"]
    if not examples:
        return ""
    formatted = "\n\n".join(
        f"Example post (highly rated by this user):\n{ex}" for ex in examples
    )
    return f"\n\nHere are examples of posts this developer has written that performed well. Match their voice, tone, and style closely:\n\n{formatted}"

def _plan_block(payload: Optional[dict] = None) -> str:
    plan = "free"
    if payload and "twitter_plan" in payload:
        plan = payload["twitter_plan"]
    if plan == "premium":
        return "\n\nUser Plan: X Premium. You are NOT limited to 280 characters. Feel free to write longer, high-value posts (up to 4000 characters) if the context warrants it."
    else:
        return "\n\nUser Plan: X Free/Basic. You MUST stay under 280 characters for the main post."

# ── Base rules applied to every prompt ───────────────────────────────────────
BASE_RULES = """
Rules:
- Write in first person as the developer.
- Sound human — like a developer talking to other
  developers, not a press release or marketing copy.
- NEVER invent a project, feature, or narrative that
  isn't directly supported by the git diff, OCR text,
  or the developer's raw thought. If the available
  context is thin or unclear, write a short, honest,
  low-key post rather than fabricating details.
- If a git diff is provided, it is the primary source of truth. Screen text is secondary and may be noisy — ignore any browser UI text.
- If OCR text looks like browser UI, tab names, or
  garbled text rather than code, IGNORE it completely
  and rely only on the raw thought and git diff.
- No hashtags unless they appear naturally. Never
  more than two. Never hashtag stuff like #innovation,
  #GamingEvolved, #TechMeetsTradition — these read as
  AI-generated marketing fluff.
- No generic filler: "excited to share", "game changer",
  "cutting-edge", "pushing boundaries", "unparalleled",
  "the intersection of X and Y", "delving into".
- NEVER use marketing-heavy, hype-filled, or clickbait phrases like "Revolutionizing Snake Game Development", "unprecedented performance gains", "Join the conversation", or similar corporate/AI clichés.
- Keep it grounded and specific. Vague posts get ignored.
- If there is a code snippet in the context, reference
  the actual function name, variable, or error.
"""

# ── Prompt Loading ───────────────────────────────────────────────────────────
def load_prompt_definitions() -> dict:
    """Loads prompt templates from the JSON store or falls back to defaults."""
    prompts_path = Path("storage/data/prompts.json")
    if prompts_path.exists():
        try:
            with open(prompts_path, "r", encoding="utf-8") as f:
                stored = json.load(f)
                return {**DEFAULT_DEFINITIONS, **stored}
        except Exception as e:
            print(f"[Prompts] Error loading prompts.json: {e}")
    return DEFAULT_DEFINITIONS.copy()

def get_prompt(format_key: str, payload: Optional[dict] = None) -> str:
    """Returns the fully assembled system prompt for a given format key."""
    if format_key == "sprint_summary":
        num_captures = payload.get("num_captures", 3) if payload else 3
        return sprint_summary_prompt(num_captures, payload)

    # Map external keys to internal definitions if they differ
    key_mapping = {
        "x_post": "deep_tech",
        "pr_desc": "pr_generator",
    }
    mapped_key = key_mapping.get(format_key, format_key)
    
    pattern = get_viral_pattern(mapped_key)
    
    definitions = load_prompt_definitions()
    if mapped_key in definitions:
        template = definitions[mapped_key]["system_prompt"]
    elif mapped_key in PROMPT_MAP:
        func_name = PROMPT_MAP[mapped_key]
        if func_name == "linkedin_post_prompt":
            template = linkedin_post_prompt()
        elif func_name == "article_prompt":
            template = article_prompt()
        else:
            template = ""
    else:
        template = f"You are a developer writing a {format_key} post."
    
    plan_block = _plan_block(payload) if format_key not in ["linkedin", "pr_generator", "pr_desc", "article"] else ""
    prompt = f"{template}\n\n{pattern}\n\n{BASE_RULES}{_narrative_block(payload)}{_tone_block(payload)}{plan_block}"
    return prompt

def get_all_prompts(payload: Optional[dict] = None) -> dict[str, str]:
    """Returns all prompts as a dict for parallel generation."""
    definitions = load_prompt_definitions()
    prompts = {key: get_prompt(key, payload) for key in definitions.keys() if key != "sprint_summary"}
    
    if "linkedin" not in prompts:
        prompts["linkedin"] = get_prompt("linkedin", payload)
    if "article" not in prompts:
        prompts["article"] = get_prompt("article", payload)
        
    return prompts

# ── Specialized Prompts ───────────────────────────────────────────────────────
def linkedin_post_prompt() -> str:
    """Professional but human LinkedIn post prompt template."""
    return """You are a developer writing a professional but human post for LinkedIn.

Your goal is to share a technical win or insight in a way that builds your professional brand without sounding like a corporate robot. LinkedIn posts perform best with white space, a strong hook, and a personal narrative.

IMPORTANT: Prioritize the developer's raw thought/prompt if one is provided. Even if the developer's thought/prompt is brief, you MUST elaborate extensively, explaining the project narrative, technical context, challenges, choices, and what it unlocks next. Do NOT write a short 2-3 sentence post. Your output MUST meet the target length of 800–1300 characters.

Format guidance:
- Hook: Line 1 must be a compelling one-sentence hook that stops the scroll.
- The Story: Explain the technical context, the challenge, and how you solved it. Use line breaks for readability.
- The Insight: Share one high-level takeaway that other professionals (not just devs) can appreciate.
- CTA: End with a call to action or a question to your network.
- No hashtag spam (max 3). No generic 'thrilled to announce' filler.

Character target: 800–1300 characters."""

def article_prompt(codebase_summary: str = "") -> str:
    """Generates a full Medium-ready markdown article template."""
    codebase_block = f"\n\nCodebase Summary:\n{codebase_summary}" if codebase_summary else ""
    return f"""You are a developer writing a full Medium-ready technical article in Markdown.

Your goal is to turn the current sprint context and raw thoughts into a structured, high-value technical article that documents your journey and teaches a specific lesson.

Sections to include:
1. Hook: A dramatic opener about the problem or the struggle.
2. Context: What you were building and why it matters.
3. The Journey: The key moments, decisions, and breakthroughs from the logs.
4. Technical Detail: Deep dive into the implementation. Use code snippets from the git diff.
5. Resolution: What is now built and working that wasn't before? What does it unlock?
6. Takeaway: One specific thing other developers can apply to their own work.

Target length: 800–1500 words. Be comprehensive and use Markdown formatting for headers, lists, and code blocks.{codebase_block}"""

# ── Sprint Mode batch prompt ──────────────────────────────────────────────────
def sprint_summary_prompt(num_captures: int, payload: Optional[dict] = None) -> str:
    return f"""You are a developer writing a build thread for X (Twitter) that covers an entire coding sprint.

You have been given a log of {num_captures} separate captures made during a focused sprint — each containing a git diff, OCR context, and a short raw thought. Your job is to synthesise them into one compelling narrative thread that tells the full story of the sprint.

Format guidance:
- Tweet 1: The hook. What was the mission of this sprint? What problem were you trying to solve? Make someone stop scrolling.
- Tweets 2–4: The build story. Pick the 3 most interesting moments from the log — a key decision, a hard bug, a breakthrough. One tweet per moment. Be specific and sequential.
- Tweet 5: The outcome. What is now built and working that wasn't before? What does it unlock?
- Final tweet: One honest reflection — what would you do differently, what surprised you, or what is next?

Rules:
- Each tweet must stand alone but flow naturally into the next.
- Number each tweet: 1/, 2/, 3/ etc.
- Never use "excited to share" or "amazing journey". This is a war report, not a LinkedIn post.
- Specific details from the log (actual function names, error messages, time spent) make this format work. Use them.
- Total thread length: 6–7 tweets.

{BASE_RULES}{_narrative_block(payload)}{_tone_block(payload)}"""

# ── User message builder ──────────────────────────────────────────────────────
def build_user_message(payload: dict) -> str:
    """
    Builds the user-turn message that gets sent to the LLM.
    Structures raw thoughts, git diff, OCR screen text, and project context.
    """
    if payload.get("user_message"):
        return payload["user_message"]
    
    parts = []
    parts.append("Here is the context for this build update:\n")

    raw_thought = payload.get("raw_thought", "").strip()
    if raw_thought:
        parts.append(f"## Developer's raw thought\n{raw_thought}")

    git_diff = payload.get("git_diff", "").strip()
    if git_diff:
        parts.append(f"## Git diff (primary source)\n```\n{git_diff}\n```")

    ocr_text = payload.get("ocr_text", "").strip()
    use_vision = payload.get("use_vision_fallback", False)
    if ocr_text and not use_vision:
        parts.append(f"## Screen text (secondary, may be noisy)\n{ocr_text}")

    narrative = payload.get("narrative", "").strip()
    if narrative:
        parts.append(f"## Project context\n{narrative}")

    parts.append(
        "\nUsing the context above, generate the post now. "
        "Follow the format and rules in the system prompt exactly."
    )
    return "\n\n".join(parts)
