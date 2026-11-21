import time
import streamlit as st

st.set_page_config(page_title="Number Hunt Game", page_icon="🎯", layout="centered")

MIN_VAL = 1
MAX_VAL = 1000
TIME_LIMIT_SECONDS = 60
CREDITS = "Developed by Qazi Mudassar Ilyas & ChatGPT"

st.markdown(
    """
    <style>
    .block-container {
        max-width: 720px;
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .credits-banner {
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        color: #4f46e5;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        border-radius: 10px;
        padding: 0.45rem 0.9rem;
        margin-bottom: 1rem;
    }
    .guess-card {
        text-align: center;
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 1.25rem 1rem;
        margin: 0.75rem 0 1rem 0;
        box-shadow: 0 6px 18px rgba(30, 27, 75, 0.16);
    }
    .guess-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.85;
        margin-bottom: 0.25rem;
    }
    .guess-number {
        font-size: clamp(2.4rem, 7vw, 3.6rem);
        font-weight: 800;
        line-height: 1.1;
    }
    div.stButton > button {
        min-height: 3.1rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
    }
    @media (max-width: 640px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }
        div.stButton > button {
            min-height: 3.4rem;
            font-size: 1.05rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state(screen: str = "home") -> None:
    st.session_state.screen = screen
    st.session_state.low = MIN_VAL
    st.session_state.high = MAX_VAL
    st.session_state.guesses = 0
    st.session_state.guess = (MIN_VAL + MAX_VAL) // 2
    st.session_state.start_time = time.time() if screen == "playing" else None
    st.session_state.outcome = None  # "won" | "timeout" | "contradiction"
    st.session_state.last_feedback = None


def remaining_seconds() -> int:
    if st.session_state.start_time is None:
        return TIME_LIMIT_SECONDS
    elapsed = time.time() - st.session_state.start_time
    return max(0, int(TIME_LIMIT_SECONDS - elapsed))


def format_range(low: int, high: int) -> str:
    return f"{low} – {high}" if low <= high else "Empty"


def make_next_guess() -> None:
    if st.session_state.low > st.session_state.high:
        st.session_state.outcome = "contradiction"
        st.session_state.screen = "ended"
        return
    st.session_state.guess = (st.session_state.low + st.session_state.high) // 2
    st.session_state.guesses += 1


def start_game() -> None:
    init_state(screen="playing")
    st.session_state.guesses = 1
    st.session_state.guess = (MIN_VAL + MAX_VAL) // 2
    st.session_state.start_time = time.time()


def handle_response(choice: str) -> None:
    if remaining_seconds() <= 0:
        st.session_state.outcome = "timeout"
        st.session_state.screen = "ended"
        return

    current = st.session_state.guess
    if choice == "Correct":
        st.session_state.last_feedback = f"Marked **{current}** as Correct."
        st.session_state.outcome = "won"
        st.session_state.screen = "ended"
        return
    if choice == "Too low":
        st.session_state.low = current + 1
        st.session_state.last_feedback = (
            f"**{current}** was **Too low** → new range is **{format_range(st.session_state.low, st.session_state.high)}**."
        )
    elif choice == "Too high":
        st.session_state.high = current - 1
        st.session_state.last_feedback = (
            f"**{current}** was **Too high** → new range is **{format_range(st.session_state.low, st.session_state.high)}**."
        )

    make_next_guess()


if "screen" not in st.session_state:
    init_state("home")


def render_header() -> None:
    st.markdown("## 🎯 Number Hunt Game")
    st.markdown(f'<div class="credits-banner">{CREDITS}</div>', unsafe_allow_html=True)


def render_home() -> None:
    render_header()
    st.markdown(
        """
        - **Think secretly:** Pick any integer from **1 to 1,000** in your head — **do not type or enter it**.
        - **Race the clock:** The computer starts at the midpoint and has **60 seconds** to find your number.
        - **Guide each guess:** Tap **Too low**, **Too high**, or **Correct** after every guess.
        - **Binary search:** Each answer halves the remaining range until solved, timed out, or contradictory.
        """
    )
    if st.button("Start Game", type="primary", use_container_width=True):
        start_game()
        st.rerun()


def render_playing() -> None:
    render_header()

    secs_left = remaining_seconds()
    if secs_left <= 0:
        st.session_state.outcome = "timeout"
        st.session_state.screen = "ended"
        st.rerun()

    m1, m2, m3 = st.columns(3)
    m1.metric("Attempts", st.session_state.guesses)
    m2.metric("Possible Range", format_range(st.session_state.low, st.session_state.high))
    m3.metric("Time Left", f"{secs_left}s")

    st.markdown(
        f"""
        <div class="guess-card">
            <div class="guess-label">Computer's Current Guess</div>
            <div class="guess-number">{st.session_state.guess}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.last_feedback:
        st.info(st.session_state.last_feedback)

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Too low", use_container_width=True):
            handle_response("Too low")
            st.rerun()
    with b2:
        if st.button("Too high", use_container_width=True):
            handle_response("Too high")
            st.rerun()
    with b3:
        if st.button("Correct", type="primary", use_container_width=True):
            handle_response("Correct")
            st.rerun()

    if st.button("Restart Game", use_container_width=True):
        start_game()
        st.rerun()

    time.sleep(1)
    if st.session_state.screen == "playing":
        st.rerun()


def render_ended() -> None:
    render_header()
    outcome = st.session_state.outcome
    total_guesses = st.session_state.guesses

    if outcome == "won":
        st.success(
            f"Guessed your number (**{st.session_state.guess}**) in "
            f"**{total_guesses}** {'attempt' if total_guesses == 1 else 'attempts'}!"
        )
    elif outcome == "timeout":
        st.warning(
            "Time ran out before **Correct** was selected — the computer does not confirm knowing your secret number."
        )
    elif outcome == "contradiction":
        st.error(
            "Contradictory feedback detected: the remaining range became empty, so no integer fits all responses."
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Attempts", total_guesses)
    c2.metric("Last Guess", st.session_state.guess)
    c3.metric("Final Range", format_range(st.session_state.low, st.session_state.high))

    if st.button("Play Again", type="primary", use_container_width=True):
        init_state("home")
        st.rerun()


if st.session_state.screen == "home":
    render_home()
elif st.session_state.screen == "playing":
    render_playing()
else:
    render_ended()