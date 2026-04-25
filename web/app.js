const PAGE = document.body.dataset.page;

const FORM_SECTIONS = [
  {
    title: "基本資料",
    description: "這些欄位描述你的基本代謝背景與社會條件。",
    fields: [
      { name: "BMI", type: "number", step: "0.1", min: 10, max: 80, label: "BMI", hint: "如果你不知道 BMI，可以先用上面的工具算，再一鍵帶入。" },
      { name: "Age", type: "number", min: 0, max: 120, label: "年齡", hint: "請直接輸入實際年齡，嬰幼兒到高齡者都可以填。" },
      { name: "Education", type: "select", label: "教育程度", hint: "請選擇最接近的教育程度。" },
      { name: "Income", type: "select", label: "年收入等級", hint: "這是年收入區間，已依原始資料集級距換算成新台幣約略級距。" },
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
    ],
  },
];

const BINARY_OPTIONS = [
  { value: "0", label: "否" },
  { value: "1", label: "是" },
];

const ORDINAL_OPTIONS = {
  Education: [
    ["1", "未曾就學"], ["2", "國小"], ["3", "國中"], ["4", "高中"], ["5", "大學"], ["6", "研究所以上"],
  ],
  Income: [
    ["1", "年收入低於新台幣 32 萬元"], ["2", "年收入約新台幣 32-48 萬元"],
    ["3", "年收入約新台幣 48-64 萬元"], ["4", "年收入約新台幣 64-80 萬元"],
    ["5", "年收入約新台幣 80-112 萬元"], ["6", "年收入約新台幣 112-160 萬元"],
    ["7", "年收入約新台幣 160-240 萬元"], ["8", "年收入新台幣 240 萬元以上"],
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
  GenHlth: 3,
  MentHlth: 4,
  PhysHlth: 8,
  DiffWalk: 0,
  Age: 60,
  Education: 5,
  Income: 6,
};

function getBmiLevel(value) {
  if (value < 18.5) return "過輕";
  if (value < 24) return "正常";
  if (value < 27) return "過重";
  if (value < 30) return "輕度肥胖";
  if (value < 35) return "中度肥胖";
  return "重度肥胖";
}

function getBmiTone(value) {
  if (value < 18.5) return "watch";
  if (value < 24) return "good";
  if (value < 27) return "watch";
  return "risk";
}

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
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "請選擇";
    input.appendChild(placeholder);
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

function updateBmiHelper() {
  const heightInput = document.getElementById("bmiHeight");
  const weightInput = document.getElementById("bmiWeight");
  const bmiValue = document.getElementById("bmiCalculatedValue");
  const bmiHint = document.getElementById("bmiCalculatedHint");
  const bmiBadge = document.getElementById("bmiCalculatedBadge");

  if (!heightInput || !weightInput || !bmiValue || !bmiHint || !bmiBadge) return;

  const height = Number(heightInput.value);
  const weight = Number(weightInput.value);
  if (!height || !weight || height <= 0 || weight <= 0) {
    bmiValue.textContent = "--";
    bmiHint.textContent = "輸入身高與體重後，系統會自動算出 BMI。";
    bmiBadge.textContent = "等待輸入";
    bmiBadge.className = "bmi-badge neutral";
    return;
  }

  const bmi = weight / ((height / 100) ** 2);
  const level = getBmiLevel(bmi);
  const tone = getBmiTone(bmi);
  bmiValue.textContent = bmi.toFixed(1);
  bmiHint.textContent = `目前屬於「${level}」區間。你可以先把這個結果帶入問卷，再繼續做風險評估。`;
  bmiBadge.textContent = level;
  bmiBadge.className = `bmi-badge ${tone}`;
}

function initBmiHelper() {
  const heightInput = document.getElementById("bmiHeight");
  const weightInput = document.getElementById("bmiWeight");
  const fillButton = document.getElementById("fillCalculatedBmi");
  const bmiInput = document.getElementById("BMI");
  if (!heightInput || !weightInput || !fillButton || !bmiInput) return;

  heightInput.addEventListener("input", updateBmiHelper);
  weightInput.addEventListener("input", updateBmiHelper);

  fillButton.addEventListener("click", () => {
    const value = document.getElementById("bmiCalculatedValue").textContent;
    if (!value || value === "--") return;
    bmiInput.value = value;
    bmiInput.dispatchEvent(new Event("input"));
  });
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

    const topline = document.createElement("div");
    topline.className = "attention-topline";

    const title = document.createElement("strong");
    title.textContent = point.title;

    const tag = document.createElement("span");
    tag.className = "severity-tag";
    tag.dataset.severity = point.severity;
    tag.textContent = point.severity === "high" ? "優先注意" : "建議留意";

    const detail = document.createElement("p");
    detail.textContent = point.detail;

    topline.append(title, tag);
    item.append(topline, detail);
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

    const topline = document.createElement("div");
    topline.className = "recommendation-topline";

    const title = document.createElement("strong");
    title.textContent = recommendation.title;

    const tag = document.createElement("span");
    tag.className = "priority-tag";
    tag.dataset.priority = recommendation.priority;
    tag.textContent = recommendation.priority === "high" ? "優先處理" : recommendation.priority === "medium" ? "值得安排" : "持續維持";

    const description = document.createElement("p");
    description.textContent = recommendation.description;

    topline.append(title, tag);
    item.append(topline, description);
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
    const labelElement = document.createElement("span");
    labelElement.textContent = label;
    const valueElement = document.createElement("strong");
    valueElement.textContent = value;
    item.append(labelElement, valueElement);
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
  document.getElementById("resultPercentText").textContent = `${Math.round(result.risk_probability * 100)}%`;
  document.getElementById("disclaimerText").textContent = result.disclaimer;

  setRiskVisual(result.risk_probability, result.risk_level, result.risk_token);
  renderAttentionPoints(result.attention_points);
  renderRecommendations(result.recommendations);
}

function renderAboutPage() {
  const container = document.getElementById("aboutModelInfo");
  if (!container) return;

  const items = [
    "資料來源是 BRFSS 2015 糖尿病健康指標資料，共約 25 萬筆紀錄。",
    "目前使用準確率最高的校準式梯度提升分類模型，並和隨機森林、邏輯斯迴歸做過比較。",
    "模型使用 15 個輸入欄位，涵蓋病史、生活習慣、身體狀況與基本背景資料。",
    "網站顯示的是風險機率與風險分級，不是醫師診斷結果。",
  ];

  container.innerHTML = "";
  items.forEach((text) => {
    const item = document.createElement("div");
    item.className = "about-note";
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    item.appendChild(paragraph);
    container.appendChild(item);
  });
}

function initAssessmentPage() {
  renderQuestionnaire();
  initBmiHelper();

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
