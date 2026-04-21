const PAGE = document.body.dataset.page;

const FORM_SECTIONS = [
  {
    title: "基本資料",
    description: "這些欄位描述你的基本代謝背景與社會條件。",
    fields: [
      { name: "BMI", type: "number", step: "0.1", min: 10, max: 80, label: "BMI", hint: "例如 22.5、31.4。通常高於 25 就需要開始留意。" },
      { name: "Age", type: "select", label: "年齡組別", hint: "資料集使用年齡分組而不是實際歲數。" },
      { name: "Education", type: "select", label: "教育程度", hint: "請選擇最接近的教育程度。" },
      { name: "Income", type: "select", label: "收入等級", hint: "請依資料集收入區間選擇。" },
    ],
  },
  {
    title: "慢性病與病史",
    description: "這些欄位與心血管代謝風險常一起出現。",
    fields: [
      { name: "HighBP", type: "select", label: "是否有高血壓", hint: "若曾被醫師告知血壓偏高，請選擇是。" },
      { name: "HighChol", type: "select", label: "是否有高膽固醇", hint: "若曾被醫師告知高膽固醇，請選擇是。" },
      { name: "Stroke", type: "select", label: "是否曾中風", hint: "過往病史會影響整體風險估計。" },
      { name: "HeartDiseaseorAttack", type: "select", label: "是否曾有心臟病或心肌梗塞", hint: "請依照實際病史作答。" },
    ],
  },
  {
    title: "生活習慣",
    description: "這些是最常被拿來做風險改善建議的欄位。",
    fields: [
      { name: "Smoker", type: "select", label: "是否吸菸", hint: "若有規律吸菸習慣，請選擇是。" },
      { name: "PhysActivity", type: "select", label: "是否規律運動", hint: "包含快走、健身、球類或其他持續活動。" },
      { name: "HvyAlcoholConsump", type: "select", label: "是否重度飲酒", hint: "若長期飲酒量偏高，建議如實填寫。" },
    ],
  },
  {
    title: "健康狀況",
    description: "這組欄位用來描述你近期的健康感受與就醫狀況。",
    fields: [
      { name: "GenHlth", type: "select", label: "自評整體健康", hint: "1 是極佳，5 是很差。" },
      { name: "MentHlth", type: "number", min: 0, max: 30, label: "過去 30 天心理不佳天數", hint: "請填 0 到 30 之間的整數。" },
      { name: "PhysHlth", type: "number", min: 0, max: 30, label: "過去 30 天身體不佳天數", hint: "例如疲勞、疼痛、不舒服等天數。" },
      { name: "DiffWalk", type: "select", label: "是否行走困難", hint: "若走路或爬樓梯有明顯困難，請選擇是。" },
      { name: "NoDocbcCost", type: "select", label: "是否曾因費用無法就醫", hint: "這個欄位會反映醫療可近性。" },
    ],
  },
];

const BINARY_OPTIONS = [
  { value: "0", label: "否" },
  { value: "1", label: "是" },
];

const ORDINAL_OPTIONS = {
  Age: [
    ["1", "18-24歲"], ["2", "25-29歲"], ["3", "30-34歲"], ["4", "35-39歲"],
    ["5", "40-44歲"], ["6", "45-49歲"], ["7", "50-54歲"], ["8", "55-59歲"],
    ["9", "60-64歲"], ["10", "65-69歲"], ["11", "70-74歲"], ["12", "75-79歲"], ["13", "80歲以上"],
  ],
  Education: [
    ["1", "未曾就學"], ["2", "國小"], ["3", "國中"], ["4", "高中"], ["5", "大學"], ["6", "研究所以上"],
  ],
  Income: [
    ["1", "低於 10,000 美元"], ["2", "10,000-14,999 美元"], ["3", "15,000-19,999 美元"], ["4", "20,000-24,999 美元"],
    ["5", "25,000-34,999 美元"], ["6", "35,000-49,999 美元"], ["7", "50,000-74,999 美元"], ["8", "75,000 美元以上"],
  ],
  GenHlth: [
    ["1", "極佳"], ["2", "很好"], ["3", "普通"], ["4", "較差"], ["5", "很差"],
  ],
};

const DEMO_PAYLOAD = {
  HighBP: 1,
  HighChol: 1,
  BMI: 31.5,
  Smoker: 0,
  Stroke: 0,
  HeartDiseaseorAttack: 0,
  PhysActivity: 1,
  HvyAlcoholConsump: 0,
  NoDocbcCost: 0,
  GenHlth: 3,
  MentHlth: 4,
  PhysHlth: 8,
  DiffWalk: 0,
  Age: 9,
  Education: 5,
  Income: 6,
};

function createField(field) {
  const wrapper = document.createElement("div");
  wrapper.className = "field";

  const label = document.createElement("label");
  label.setAttribute("for", field.name);
  label.textContent = field.label;
  wrapper.appendChild(label);

  let input;
  if (field.type === "select") {
    input = document.createElement("select");
    input.innerHTML = `<option value="">請選擇</option>`;
    const options = ORDINAL_OPTIONS[field.name] || BINARY_OPTIONS.map(({ value, label: optionLabel }) => [value, optionLabel]);
    options.forEach(([value, optionLabel]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = optionLabel;
      input.appendChild(option);
    });
  } else {
    input = document.createElement("input");
    input.type = "number";
    input.step = field.step || "1";
    input.min = field.min;
    input.max = field.max;
    input.placeholder = `${field.min} - ${field.max}`;
  }

  input.name = field.name;
  input.id = field.name;
  input.required = true;
  wrapper.appendChild(input);

  const hint = document.createElement("small");
  hint.textContent = field.hint;
  wrapper.appendChild(hint);

  return wrapper;
}

function renderQuestionnaire() {
  const sectionsContainer = document.getElementById("questionnaireSections");
  if (!sectionsContainer) return;

  FORM_SECTIONS.forEach((section) => {
    const sectionElement = document.createElement("section");
    sectionElement.className = "form-section";

    const title = document.createElement("h3");
    title.textContent = section.title;
    sectionElement.appendChild(title);

    const description = document.createElement("p");
    description.textContent = section.description;
    sectionElement.appendChild(description);

    const fieldGrid = document.createElement("div");
    fieldGrid.className = "field-grid";
    section.fields.forEach((field) => fieldGrid.appendChild(createField(field)));
    sectionElement.appendChild(fieldGrid);

    sectionsContainer.appendChild(sectionElement);
  });
}

function collectPayload() {
  const payload = {};
  for (const section of FORM_SECTIONS) {
    for (const field of section.fields) {
      const element = document.getElementById(field.name);
      if (!element.value) {
        throw new Error(`請完成欄位：${field.label}`);
      }
      payload[field.name] = Number(element.value);
    }
  }
  return payload;
}

function fillDemo() {
  Object.entries(DEMO_PAYLOAD).forEach(([key, value]) => {
    const element = document.getElementById(key);
    if (element) {
      element.value = value;
    }
  });
}

function setRiskVisual(probability, riskLevel, token) {
  const gauge = document.getElementById("riskGauge");
  const progress = document.getElementById("gaugeProgress");
  const riskPercent = document.getElementById("riskPercent");
  const riskLevelElement = document.getElementById("riskLevel");
  if (!gauge || !progress || !riskPercent || !riskLevelElement) return;

  riskPercent.textContent = `${Math.round(probability * 100)}%`;
  riskLevelElement.textContent = riskLevel;
  riskLevelElement.dataset.tone = token;
  gauge.dataset.tone = token;

  const radius = 78;
  const circumference = 2 * Math.PI * radius;
  progress.style.strokeDasharray = `${circumference}`;
  progress.style.strokeDashoffset = `${circumference * (1 - probability)}`;

  document.querySelectorAll(".risk-legend span").forEach((item) => {
    item.classList.toggle("active", item.dataset.tone === token);
  });
}

function renderAttentionPoints(points) {
  const container = document.getElementById("attentionPoints");
  if (!container) return;
  container.innerHTML = "";

  points.forEach((point) => {
    const item = document.createElement("article");
    item.className = "attention-item";
    item.dataset.severity = point.severity;
    item.innerHTML = `
      <div class="attention-topline">
        <strong>${point.title}</strong>
        <span class="severity-tag" data-severity="${point.severity}">${point.severity === "high" ? "優先注意" : "建議留意"}</span>
      </div>
      <p>${point.detail}</p>
    `;
    container.appendChild(item);
  });
}

function renderRecommendations(recommendations) {
  const container = document.getElementById("recommendations");
  if (!container) return;
  container.innerHTML = "";

  recommendations.forEach((recommendation) => {
    const item = document.createElement("article");
    item.className = "recommendation-item";
    item.innerHTML = `
      <div class="recommendation-topline">
        <strong>${recommendation.title}</strong>
        <span class="priority-tag" data-priority="${recommendation.priority}">
          ${recommendation.priority === "high" ? "優先處理" : recommendation.priority === "medium" ? "值得安排" : "持續維持"}
        </span>
      </div>
      <p>${recommendation.description}</p>
    `;
    container.appendChild(item);
  });
}

function renderInputSummary(inputSummary) {
  const container = document.getElementById("inputSummary");
  if (!container) return;
  container.innerHTML = "";

  Object.entries(inputSummary).forEach(([label, value]) => {
    const item = document.createElement("div");
    item.className = "summary-chip";
    item.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    container.appendChild(item);
  });
}

function persistResult(result) {
  sessionStorage.setItem("latestPrediction", JSON.stringify(result));
}

function readPersistedResult() {
  const raw = sessionStorage.getItem("latestPrediction");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (_error) {
    return null;
  }
}

function renderResultPage(result) {
  const panel = document.getElementById("resultsPanel");
  const emptyState = document.getElementById("emptyState");
  if (!panel) return;

  panel.classList.remove("hidden");
  if (emptyState) emptyState.classList.add("hidden");

  document.getElementById("predictedClass").textContent = result.result_summary;
  document.getElementById("resultRiskLevel").textContent = result.risk_level;
  document.getElementById("disclaimerText").textContent = result.disclaimer;

  setRiskVisual(result.risk_probability, result.risk_level, result.risk_token);
  renderAttentionPoints(result.attention_points);
  renderRecommendations(result.recommendations);
  renderInputSummary(result.input_summary);
}

async function renderAboutPage() {
  const container = document.getElementById("aboutModelInfo");
  if (!container) return;

  try {
    const response = await fetch("/api/model-info");
    const info = await response.json();

    const items = [
      "這個網站會根據你的填答內容，估算目前的糖尿病風險。",
      `問答欄位來自健康指標、生活習慣與自評健康狀況。`,
      `結果頁會把預測分數轉成一般人比較容易理解的風險分級與建議。`,
    ];

    container.innerHTML = "";
    items.forEach((text) => {
      const item = document.createElement("div");
      item.className = "about-note";
      item.innerHTML = `<p>${text}</p>`;
      container.appendChild(item);
    });
  } catch (_error) {
    container.innerHTML = `<div class="about-note"><p>模型說明目前無法載入，請稍後再試。</p></div>`;
  }
}

function initAssessmentPage() {
  renderQuestionnaire();

  const formElement = document.getElementById("predictionForm");
  const formError = document.getElementById("formError");
  const fillDemoButton = document.getElementById("fillDemo");

  formElement.addEventListener("submit", async (event) => {
    event.preventDefault();
    formError.textContent = "";

    try {
      const payload = collectPayload();
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "預測失敗，請稍後再試。");
      }

      const result = await response.json();
      persistResult(result);
      window.location.href = "/result";
    } catch (error) {
      formError.textContent = error.message;
    }
  });

  fillDemoButton.addEventListener("click", fillDemo);
}

function initResultPage() {
  const result = readPersistedResult();
  if (!result) {
    document.getElementById("emptyState").classList.remove("hidden");
    return;
  }
  renderResultPage(result);
}

if (PAGE === "assessment") {
  initAssessmentPage();
}

if (PAGE === "result") {
  initResultPage();
}

if (PAGE === "about") {
  renderAboutPage();
}
