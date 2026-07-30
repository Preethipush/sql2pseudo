const sqlInput = document.getElementById("sql-input");
const pseudoOutput = document.getElementById("pseudo-output");
const detectedOutput = document.getElementById("detected-output");
const explanationOutput = document.getElementById("explanation-output");
const errorBox = document.getElementById("error-box");
const convertBtn = document.getElementById("convert-btn");
const clearBtn = document.getElementById("clear-btn");
const copyPseudoBtn = document.getElementById("copy-pseudo");
const copyExplanationBtn = document.getElementById("copy-explanation");

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

function renderDetected(detected) {
  const groups = [
    ["Tables", detected.tables],
    ["Joins", detected.joins],
    ["Conditions", detected.conditions],
    ["Order By", detected.order_by],
  ];

  const nonEmpty = groups.filter(([, values]) => values && values.length > 0);

  if (nonEmpty.length === 0) {
    detectedOutput.innerHTML = '<p class="placeholder">No objects detected.</p>';
    return;
  }

  detectedOutput.innerHTML = nonEmpty
    .map(([label, values]) => `
      <div class="detected-item">
        <div class="label">${label}</div>
        <div class="value">${values.map(escapeHtml).join(", ")}</div>
      </div>
    `)
    .join("");
}

function renderExplanation(bullets) {
  if (!bullets || bullets.length === 0) {
    explanationOutput.innerHTML = '<li class="placeholder">Nothing converted yet.</li>';
    return;
  }
  explanationOutput.innerHTML = bullets.map((b) => `<li>${escapeHtml(b)}</li>`).join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function convert() {
  const sql = sqlInput.value.trim();
  hideError();

  if (!sql) {
    showError("Please enter a SQL query.");
    return;
  }

  pseudoOutput.textContent = "Converting...";
  convertBtn.disabled = true;

  try {
    const res = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sql }),
    });
    const data = await res.json();

    if (data.status === "success") {
  pseudoOutput.textContent = data.pseudo_code;
  if (data.source === "ai") {
    errorBox.hidden = false;
    errorBox.style.background = "#eef2ff";
    errorBox.style.color = "#4338ca";
    errorBox.textContent = "⚡ " + (data.message || "Generated using AI fallback.");
  }
  renderDetected(data.detected || {});
  renderExplanation(data.explanation || []);
}else {
      pseudoOutput.textContent = "";
      showError(data.message || "Conversion failed.");
    }
  } catch (err) {
    pseudoOutput.textContent = "";
    showError("Request failed: " + err.message);
  } finally {
    convertBtn.disabled = false;
  }
}

convertBtn.addEventListener("click", convert);

clearBtn.addEventListener("click", () => {
  sqlInput.value = "";
  pseudoOutput.textContent = "Output will appear here.";
  detectedOutput.innerHTML = '<p class="placeholder">Nothing converted yet.</p>';
  explanationOutput.innerHTML = '<li class="placeholder">Nothing converted yet.</li>';
  hideError();
});

copyPseudoBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(pseudoOutput.textContent);
});

copyExplanationBtn.addEventListener("click", () => {
  const text = Array.from(explanationOutput.querySelectorAll("li")).map((li) => "- " + li.textContent).join("\n");
  navigator.clipboard.writeText(text);
});

sqlInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    convert();
  }
});
