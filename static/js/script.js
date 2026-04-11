/**
 * Virtual Lab: Detergent Making Practical
 * ========================================
 * Client-side logic for the lab simulation page.
 *
 * Responsibilities:
 *   - Capture student information before the experiment starts.
 *   - Drive the step-by-step experiment flow with animations.
 *   - Update the progress bar and process-flow diagram.
 *   - Persist progress to the Flask backend via Fetch API.
 *   - Show a completion certificate when all steps are done.
 */

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Ordered list of experiment steps (must match backend VALID_STEPS). */
const STEPS = [
    "Neutralization",
    "Mixing",
    "Additives",
    "Drying",
    "Packaging",
];

/** Duration (ms) each animation plays before the step is marked done. */
const ANIMATION_DURATION = 3000;

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

/** Index of the next step to perform (0-based). */
let currentStep = 0;

/** Student details captured from the form. */
let studentName = "";
let studentClass = "";

// ---------------------------------------------------------------------------
// DOM references (resolved after DOMContentLoaded)
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    const studentForm = document.getElementById("studentForm");
    if (studentForm) {
        studentForm.addEventListener("submit", handleStudentFormSubmit);
    }
});

// ---------------------------------------------------------------------------
// Student Form
// ---------------------------------------------------------------------------

/**
 * Handle the student-info form submission.
 * Validates inputs, hides the form panel, and reveals the lab workspace.
 */
function handleStudentFormSubmit(event) {
    event.preventDefault();

    const nameInput = document.getElementById("studentName");
    const classInput = document.getElementById("studentClass");

    studentName = nameInput.value.trim();
    studentClass = classInput.value.trim();

    if (!studentName || !studentClass) {
        alert("Please fill in both your name and class.");
        return;
    }

    // Try to load any existing progress for this student
    loadExistingProgress();

    // Transition UI
    document.getElementById("studentInfoPanel").style.display = "none";
    document.getElementById("labWorkspace").style.display = "block";

    // Unlock the first step
    unlockStep(0);
}

// ---------------------------------------------------------------------------
// Progress Persistence (Fetch API)
// ---------------------------------------------------------------------------

/**
 * POST the current step to the backend so it is stored in the database.
 *
 * @param {string} stepName - The step that was just completed.
 */
function saveProgress(stepName) {
    fetch("/save-progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: studentName,
            class: studentClass,
            step_completed: stepName,
        }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                console.error("Save-progress error:", data.error);
            } else {
                console.log("Progress saved:", data.message);
            }
        })
        .catch((err) => console.error("Network error:", err));
}

/**
 * Load any existing progress for the student from the backend.
 * If the student has a prior record, fast-forward the UI.
 */
function loadExistingProgress() {
    fetch(`/get-progress?name=${encodeURIComponent(studentName)}`)
        .then((res) => res.json())
        .then((data) => {
            if (data.success && data.data) {
                const savedStep = data.data.step_completed;
                const savedIndex = STEPS.indexOf(savedStep);
                if (savedIndex >= 0) {
                    // Fast-forward completed steps without animation
                    for (let i = 0; i <= savedIndex; i++) {
                        markStepDone(i, /* animate */ false);
                    }
                    currentStep = savedIndex + 1;
                    updateProgressBar();
                    updateFlowDiagram();

                    if (currentStep < STEPS.length) {
                        unlockStep(currentStep);
                    } else {
                        showCompletion();
                    }
                }
            }
        })
        .catch((err) => console.error("Load progress error:", err));
}

// ---------------------------------------------------------------------------
// Step Execution
// ---------------------------------------------------------------------------

/**
 * Called when the user clicks "Perform Step" for a given step index.
 * Triggers the animation, disables the button, saves progress, and
 * advances to the next step after the animation completes.
 *
 * @param {number} stepIndex - Zero-based step index.
 */
function performStep(stepIndex) {
    if (stepIndex !== currentStep) return;

    const btn = document.getElementById(`btn-${stepIndex}`);
    const card = document.getElementById(`step-${stepIndex}`);
    const status = document.getElementById(`status-${stepIndex}`);

    // Disable button during animation
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

    // Mark card as active
    card.classList.remove("locked");
    card.classList.add("active");
    status.textContent = "In Progress";
    status.className = "step-status status-active";

    // Run step-specific animation
    playAnimation(stepIndex);

    // After animation, finalise the step
    setTimeout(() => {
        markStepDone(stepIndex, true);
        currentStep = stepIndex + 1;
        updateProgressBar();
        updateFlowDiagram();
        saveProgress(STEPS[stepIndex]);

        // Unlock next step or show completion
        if (currentStep < STEPS.length) {
            unlockStep(currentStep);
        } else {
            showCompletion();
        }
    }, ANIMATION_DURATION);
}

// ---------------------------------------------------------------------------
// UI Helpers
// ---------------------------------------------------------------------------

/**
 * Unlock a step card so the user can interact with it.
 *
 * @param {number} idx - Step index.
 */
function unlockStep(idx) {
    const card = document.getElementById(`step-${idx}`);
    const btn = document.getElementById(`btn-${idx}`);
    const status = document.getElementById(`status-${idx}`);

    if (!card) return;

    card.classList.remove("locked");
    card.classList.add("active");

    // Show step body
    const body = card.querySelector(".step-body");
    if (body) body.style.display = "block";

    btn.disabled = false;
    btn.innerHTML = `<i class="fas fa-play"></i> Perform ${STEPS[idx]}`;

    status.textContent = "Ready";
    status.className = "step-status status-active";

    // Scroll the card into view
    card.scrollIntoView({ behavior: "smooth", block: "center" });
}

/**
 * Mark a step card as completed.
 *
 * @param {number} idx      - Step index.
 * @param {boolean} animate - Whether to run the finishing animation.
 */
function markStepDone(idx, animate) {
    const card = document.getElementById(`step-${idx}`);
    const btn = document.getElementById(`btn-${idx}`);
    const status = document.getElementById(`status-${idx}`);

    if (!card) return;

    card.classList.remove("active", "locked");
    card.classList.add("done");

    // Show step body for completed steps
    const body = card.querySelector(".step-body");
    if (body) body.style.display = "block";

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-check-circle"></i> Completed';
    btn.style.background = "#27ae60";

    status.textContent = "Completed";
    status.className = "step-status status-done";
}

/**
 * Update the overall progress bar based on currentStep.
 */
function updateProgressBar() {
    const pct = Math.round((currentStep / STEPS.length) * 100);
    const bar = document.getElementById("progressBar");
    const label = document.getElementById("progressPercent");
    if (bar) bar.style.width = pct + "%";
    if (label) label.textContent = pct + "%";
}

/**
 * Highlight the correct flow-diagram nodes based on progress.
 */
function updateFlowDiagram() {
    for (let i = 0; i < STEPS.length; i++) {
        const node = document.getElementById(`flow-${i}`);
        if (!node) continue;
        node.classList.remove("active", "completed");
        if (i < currentStep) {
            node.classList.add("completed");
        } else if (i === currentStep) {
            node.classList.add("active");
        }
    }
}

/**
 * Show the completion panel with the certificate.
 */
function showCompletion() {
    const panel = document.getElementById("completionPanel");
    if (panel) {
        panel.style.display = "block";
        panel.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    const certName = document.getElementById("certName");
    if (certName) certName.textContent = studentName;

    const certDate = document.getElementById("certDate");
    if (certDate) {
        const now = new Date();
        certDate.textContent = "Date: " + now.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "long",
            year: "numeric",
        });
    }
}

/**
 * Restart the entire experiment — reload the page.
 */
function restartExperiment() {
    window.location.reload();
}

// ---------------------------------------------------------------------------
// Step Animations
// ---------------------------------------------------------------------------

/**
 * Dispatch the correct animation for a given step index.
 *
 * @param {number} idx - Step index.
 */
function playAnimation(idx) {
    switch (idx) {
        case 0: animateNeutralization(); break;
        case 1: animateMixing();         break;
        case 2: animateAdditives();      break;
        case 3: animateDrying();         break;
        case 4: animatePackaging();      break;
    }
}

/** Step 1 — Neutralization: beaker liquid rises with bubbles. */
function animateNeutralization() {
    const resultBeaker = document.querySelector(".beaker-result");
    if (resultBeaker) {
        resultBeaker.classList.add("reacting");
    }
}

/** Step 2 — Mixing: mixer blade spins. */
function animateMixing() {
    const blade = document.getElementById("mixerBlade");
    if (blade) {
        blade.classList.add("spinning");
        // Stop spinning after animation duration
        setTimeout(() => blade.classList.remove("spinning"), ANIMATION_DURATION);
    }
}

/** Step 3 — Additives: bottles pour into the vat. */
function animateAdditives() {
    const bottles = document.querySelectorAll(".additive-bottle");
    const vatLiquid = document.querySelector(".vat-liquid");

    bottles.forEach((bottle, i) => {
        setTimeout(() => {
            bottle.classList.add("pouring");
        }, i * 500);
    });

    setTimeout(() => {
        if (vatLiquid) vatLiquid.classList.add("enriched");
    }, 1500);
}

/** Step 4 — Drying: particles fall, hot air blows, powder pile grows. */
function animateDrying() {
    const tower = document.querySelector(".dryer-tower");
    if (tower) {
        tower.classList.add("drying");
    }
}

/** Step 5 — Packaging: box moves on conveyor and seal stamps. */
function animatePackaging() {
    const box = document.getElementById("pkgBox");
    const stamp = document.getElementById("sealStamp");

    if (box) box.classList.add("moving");

    setTimeout(() => {
        if (stamp) stamp.classList.add("stamped");
    }, 1500);
}
