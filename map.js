const canvas = document.getElementById("mapCanvas");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const projection = d3.geoMercator();
const path = d3.geoPath(projection, ctx);

const mapType = [
    "Borders", "Places", "Terminals", "WaterGreen", "GreenPlaces", "Beaches", "Parking", "Church", "Buildings", "Railways", "Roads", "Water" 
];

const ruMapType = [
    "Границы", "Населенные пункты", "Терминалы", "Болота", "Инфраструктура", "Пляжи", "Парковки", "Церкви", "Здания", "Железные дороги", "Дороги", "Реки"
];

const loaderColors = [
    "#90677A", "#7e5639", "#88988a", "#9bb49f",
    "#692819", "#6F9EB2", "#355743"
];


const districts = [
    "Syk", "Uhta", "Vorkuta", "Inta", "Pechora", "Sosnogorsk", 
    "UstKulom", "Kortkeros", "Sysolskii", "Koigorodskii", 
    "Priluzsky", "TroitskoPechorsk", "Izhma", "UstCilma", 
    "Vyktyl", "Knyazhpogost", "Udorskii", "Syktyvdinskii", "Usinsk", "UstVym"
];

const colorSchemeDay = {
    /*"NameTypeOfMap": ["fillColor", "strokeColor","lineWidth"],*/
    "Borders": ["none", "#7B8D67", "5"],
    "Beaches": ["#fedac0", "#7e5639", "1"],
    "Roads": ["none", "#88988a", "1"],
    "Buildings": ["#CFB5A5", "#33403d", "1"],
    "Church": ["#e3e19c", "#6e6a3f", "1"],
    "GreenPlaces": ["#9bb49f", "#454545", "2"],
    "Parking": ["#ffeddd", "#afafaf", "1"],
    "Places": ["#ffdfdd", "#82716f", "4"],
    "Railways": ["none", "#692819", "1"],
    "Terminals": ["#787268", "#4a463f", "3"],
    "Water": ["none", "#6F9EB2", "1"],
    "WaterGreen": ["#2c4a39","#377450", "1"]
};
const colorSchemeNight = {
    /*"NameTypeOfMap": ["fillColor", "strokeColor","lineWidth"],*/
    "Borders": ["none", "#d49a4a", "5"],
    "Beaches": ["#bebeaa", "#7d6633", "1"],
    "Roads": ["none", "#666aaa", "0.5"],
    "Buildings": ["#9da4d1", "#383b54", "1"],
    "Church": ["#d0d491", "#6e6a3f", "1"],
    "GreenPlaces": ["#8eb58d", "#1b4f2c", "2"],
    "Parking": ["#d2974a", "#ad6a11", "1"],
    "Places": ["#313663", "#1d203b", "4"],
    "Railways": ["none", "#c9605d", "1"],
    "Terminals": ["#4d4582", "#1d2552", "3"],
    "Water": ["none", "#5092DC","2"],
    "WaterGreen": ["#053d35","#158077", "1"]
};

const districtCenters = {
    // Название: [[Верх][Низ]]
    "Syk": [50.8196, 61.6688],
    "Uhta": [53.6834, 63.5672],
    "Vorkuta": [64.056, 67.5],
    "Inta": [60.1356, 66.0318],
    "Pechora": [57.2396, 65.1486],
    "Sosnogorsk": [53.8819, 63.5926],
    "UstKulom": [53.6908, 61.6886],
    "Kortkeros": [52.2362, 61.8104],
    "Sysolskii": [[50.0799, 61.3986],[49,60.7286]],
    "Koigorodskii": [50.9962, 60.4406],
    "Priluzsky": [50.6075, 60.2613],
    "TroitskoPechorsk": [56.2012, 62.7085],
    "Izhma": [53.1611, 65.0051],
    "UstCilma": [[52.3529, 66.8228],[51.775, 64.760]],
    "Vyktyl": [57.3158, 63.8509],
    "Knyazhpogost": [[50.9825, 62.8741], [51.4192, 64.012]],
    "Udorskii": [[49.4339,63.560],[50.3339,64.360]],
    "Syktyvdinskii": [[50.2231, 61.6745], [50.8123, 62.0532], [50.9123,61.255],[50.5234,61.5863]],
    "Usinsk": [57.5368, 65.9933],
    "UstVym": [[50.2192, 62.312], [49.7192, 62.012]]
};

const sunIcon = `<svg width="39" height="39" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
    <image href="map/SVG/MenuButtons.svg" x="0" y="-48" width="336" height="96" />
</svg>`;

const moonIcon = `<svg width="39" height="39" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
    <image href="map/SVG/MenuButtons.svg" x="0" y="0" width="336" height="96" />
</svg>`;

let districtData = {};
let cachedData = {}; 
let buttons = {};

let lastDistrict = null;
let lastCenterGeo = null;
let mapData = null;

let zoomTransform = d3.zoomIdentity;
let hoveredFeature = null;

let darkMode = false;
let mapMode = false;
let menuButtonMode = false;
let iconMenuButtonMode = false;

let isRendering = false;


const loader = document.createElement("div");
loader.id = "loader";
loader.innerHTML = `
  <div class="spinner"></div>
`;
document.body.appendChild(loader);
spinner = loader.querySelector(".spinner");


function showLoader(type) {
  if (type === "block") {
    loader.style.opacity = "1";
    loader.style.display = "flex";
  } else {
    loader.style.opacity = "0";
    setTimeout(() => {
      loader.style.display = "none";
    }, 300);
  }
}

const tooltip = document.createElement("div");
tooltip.classList.add("tooltip");
document.body.appendChild(tooltip);
// ЛКМ
const infoBox = document.createElement("div");
infoBox.classList.add("info-box");
document.body.appendChild(infoBox);
// ПКМ
const authorBox = document.createElement("div");
authorBox.classList.add("author-box");
document.body.appendChild(authorBox);
// Бургер меню с кнопками
const menuButton = document.createElement("button");
menuButton.id = "menuButtonsToggle";
document.body.appendChild(menuButton);
// ВКЛ/ВЫКЛ Иконки
const iconMenuButton = document.createElement("button");
iconMenuButton.id = "iconMenuButtonsToggle";
document.body.appendChild(iconMenuButton);
// ВКЛ/ВЫКЛ карты
const enableAllMapsButton = document.createElement("button");
enableAllMapsButton.id = "mapsVisibleToggle";
enableAllMapsButton.title = "Включить все карты";
document.body.appendChild(enableAllMapsButton);
// Переключалка темы
const themeButton = document.createElement("button");
themeButton.id = "themeToggle";
themeButton.innerHTML = moonIcon;
document.body.appendChild(themeButton);

canvas.addEventListener("contextmenu", (event) => {
    event.preventDefault();
    authorBox.innerHTML = "<strong>Автор: Наддака Артём</strong>";
    authorBox.style.display = "block";
    authorBox.style.left = `${event.pageX + 10}px`;
    authorBox.style.top = `${event.pageY + 10}px`;
});

document.addEventListener("mousemove", () => {
    authorBox.style.display = "none";
});

themeButton.addEventListener("click", () => {
    
    darkMode = !darkMode;
    clearMap();
    document.body.style.backgroundColor = darkMode ? "#E7EAEF" : "white";
    themeButton.innerHTML = darkMode ? sunIcon : moonIcon;
    changeIconColor();
    document.body.classList.toggle('dark-mode', darkMode);
    if (darkMode){
        drawMap("map/GeoJSON/Komi.geojson", "#10133a", "#D08821", 1); // Цвет для темной темы
        loadDistrictMaps(getClosestDistrict(), colorSchemeNight);
        spinner.classList.add('dark');
    }
    else {
        
        drawMap("map/GeoJSON/Komi.geojson", "#37745B", "#8B9D77", 1);// Цвет для светлой темы
        loadDistrictMaps(getClosestDistrict(), colorSchemeDay);
        spinner.classList.remove('dark');
    }
    infoBox.style.display = "none";
    applyBoxShadows();
    updateIconButtonStyles();
    updateButtonStyles(); // Вызываем обновление стилей кнопок
});

function applyBoxShadows() {
  document.querySelectorAll(".tooltip, .author-box").forEach(el => {
    el.style.boxShadow = darkMode
      ? "inset 4px 0px rgba(255, 167, 43, 0.67)"
      : "inset 4px 0px #EDC5AB";
    el.style.backgroundColor = darkMode ? 'rgba(0,0,0,0.7)' : '#333';
  });
}

function createMapControls(mapType) {
    mapType.forEach((type, index) => {
        const iconButton = document.createElement("button");
        iconButton.id = `IconToggle_${type}`;
        iconButton.className = "icon-button";
        iconButton.style.right = `${17 + 6 * index}%`;
        iconButton.dataset.type = type;
        iconButton.dataset.state = "OFF";
        iconButton.style.display = iconMenuButtonMode ? "" : "none";

        const textButton = document.createElement("button");
        textButton.className = `text-button ${type}VisibleOFF`;
        textButton.textContent = `Включить ${ruMapType[index]}`;
        textButton.style.bottom = `${5 + 7 * index}%`;
        textButton.dataset.type = type;
        textButton.style.display = menuButtonMode ? "" : "none";

        iconButton.addEventListener("click", () => {
            const newState = iconButton.dataset.state === "ON" ? "OFF" : "ON";
            setButtonState(type, index, newState);
            updateMapMode();
        });

        textButton.addEventListener("click", () => {
            const isActive = textButton.classList.contains(`${type}VisibleON`);
            const newState = isActive ? "OFF" : "ON";
            setButtonState(type, index, newState);
            updateMapMode();
        });

        document.body.appendChild(iconButton);
        document.body.appendChild(textButton);
        buttons[type] = textButton;
    });

    enableAllMapsButton.addEventListener("click", () => {
        const anyOn = Object.values(buttons).some(btn => btn.classList.contains(`${btn.dataset.type}VisibleON`));
        const newState = !anyOn ? "ON" : "OFF";
        mapType.forEach((type, index) => setButtonState(type, index, newState));
        updateMapMode();
    });

    updateIconButtonStyles();
    updateButtonStyles();
}

function setButtonState(type, index, state) {
    const iconBtn = document.querySelector(`#IconToggle_${type}`);
    const textBtn = buttons[type];

    iconBtn.dataset.state = state;
    const isOn = state === "ON";

    textBtn.classList.toggle(`${type}VisibleON`, isOn);
    textBtn.classList.toggle(`${type}VisibleOFF`, !isOn);
    textBtn.textContent = isOn ? `Выключить ${ruMapType[index]}` : `Включить ${ruMapType[index]}`;
}


function updateIconButtonStyles() {

    
    const iconSize = 60;
    const scale = iconSize / 48;

    const spriteWidth = 576 * scale;
    const spriteHeight = 192 * scale;

    mapType.forEach((type, index) => {
        const iconBtn = document.querySelector(`#IconToggle_${type}`);
        if (!iconBtn) return;

        const state = iconBtn.dataset.state || "OFF";

        const x = index * iconSize;
        let y = 0;
        if (state === "OFF" && !darkMode) y = 0;
        else if (state === "ON" && !darkMode) y = iconSize;
        else if (state === "OFF" && darkMode) y = iconSize * 2;
        else if (state === "ON" && darkMode) y = iconSize * 3;

        iconBtn.innerHTML = "";
        iconBtn.style.width = `${iconSize}px`;
        iconBtn.style.height = `${iconSize}px`;
        iconBtn.style.backgroundImage = 'url("map/SVG/IconButtons.svg")';
        iconBtn.style.backgroundPosition = `-${x}px -${y}px`;
        iconBtn.style.backgroundSize = `${spriteWidth}px ${spriteHeight}px`;
        iconBtn.title = `${state === "OFF" ? "включить" : "выключить"} ${ruMapType[index].toLowerCase()}`;

    });
}


function updateButtonStyles() {
    Object.values(buttons).forEach(button => {
        const isActive = button.classList.contains(`${button.dataset.type}VisibleON`);
        
        button.id = darkMode ? "nightButton" : "lightButton";

        button.style.backgroundColor = isActive 
            ? (darkMode ? "rgba(33, 37, 90, 0.8)" : "#f0d3c0") 
            : (darkMode ? '' : '');

        button.style.color = isActive 
            ? (darkMode ? "white" : "black") 
            : (darkMode ? '' : '');

        button.style.boxShadow = isActive 
            ? (darkMode ? "4.5px 0px 0px inset rgba(0, 0, 0, 0.5)" : "4.5px 0px 0px inset #333") 
            : (darkMode ? "-4.5px 0px 0px inset rgba(33, 37, 90, 1)" : "-4.5px 0px 0px inset #EDC5AB");
    });
}

async function updateMapMode() {
    mapMode = Object.values(buttons).some(btn => btn.classList.contains(`${btn.dataset.type}VisibleON`));
    updateButtonStyles();
    updateIconButtonStyles();
    const district = getClosestDistrict();
    await (darkMode
        ? loadDistrictMaps(district, colorSchemeNight)
        : loadDistrictMaps(district, colorSchemeDay));
    changeIconColor();
}

menuButton.addEventListener("click", () => {
    menuButtonMode = !menuButtonMode
    mapType.forEach(name => {
        buttons[name].style.display = menuButtonMode == true ? "" : "none";
    });    
    changeIconColor(); /*"☰" : "X";*/
})

iconMenuButton.addEventListener("click", () => {
    iconMenuButtonMode = !iconMenuButtonMode
    mapType.forEach(name => {
        const iconBtn = document.getElementById(`IconToggle_${name}`);
        if (iconBtn) {
            iconBtn.style.display = iconMenuButtonMode ? "" : "none";
        }
    }); 
    changeIconColor();
})

function changeIconColor() {
    const makeIcon = (xOffset) => `
        <svg width="39" height="39" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <image href="map/SVG/MenuButtons.svg" x="${xOffset}" y="${darkMode ? -48 : 0}" width="336" height="96" />
        </svg>
    `;

    menuButton.innerHTML = makeIcon(menuButtonMode ? -96 : -48);
    enableAllMapsButton.innerHTML = makeIcon(mapMode ? -192 : -144);
    iconMenuButton.innerHTML = makeIcon(iconMenuButtonMode ? -288 : -240);
}


function drawMap(geojsonFile, fillColor, strokeColor, opacity) {
    fetch(geojsonFile)
        .then(response => response.json())
        .then(data => {
                mapData = { data, fillColor, strokeColor, opacity};
                updateProjection();

            render();
        })
        .catch(error => console.error("Ошибка загрузки GeoJSON:", error));
}

function updateProjection() {
    if (!mapData) return;
    projection.fitSize([canvas.width, canvas.height], mapData.data);
}

async function loadDistrictMaps(district, colorScheme) {
    districtData[district] = [];
    showLoader("block");
    
    for (const type of mapType) {
        
        if (type === "Buildings" && zoomTransform.k < 800) {
            const cacheKey = `${district}${type}`;
            if (cachedData[cacheKey]) {
                delete cachedData[cacheKey];
            }
            continue;
        }
        
        if ((type === "GreenPlaces" || type === "Parking") && zoomTransform.k < 300) {
            const cacheKey = `${district}${type}`;
            if (cachedData[cacheKey]) {
                delete cachedData[cacheKey];
            }
            continue;
        }

        const button = buttons[type];
        if (!button || !button.classList.contains(`${type}VisibleON`)) continue;

        const cacheKey = `${district}${type}`;
        if (!cachedData[cacheKey]) {
            try {
                const response = await fetch(`map/GeoJSON/${district}/${district}${type}.geojson`);
                if (!response.ok) throw new Error(`Ошибка загрузки ${cacheKey}`);
                cachedData[cacheKey] = await response.json();
            } catch (e) {
                console.error(e);
                continue;
            }
        }

        const features = cachedData[cacheKey].features;
        features.forEach(f => {
            const [cx, cy] = path.centroid(f);
            f._cx = cx;
            f._cy = cy;
        });

        const quadtree = d3.quadtree()
            .x(f => f._cx)
            .y(f => f._cy)
            .addAll(features);

        districtData[district].push({
            data: cachedData[cacheKey],
            fillColor: colorScheme[type][0],
            strokeColor: colorScheme[type][1],
            lineWidth: colorScheme[type][2],
            opacity: 0.8,
            quadtree
        });
    }
    showLoader("none");
}

async function updateDistrictCenters() {
    for (const district of districts) {
        try {
            const response = await fetch(`map/GeoJSON/${district}/${district}Borders.geojson`);
            if (!response.ok) throw new Error(`Не удалось загрузить ${district}Borders.geojson`);
            
            const geojson = await response.json();
            districtCenters[district] = [];
            
            geojson.features.forEach(feature => {
                if (feature.geometry.type === "Polygon") {
                    districtCenters[district].push(feature.geometry.coordinates[0].filter((_, i) => i % 10 === 0));
                } else if (feature.geometry.type === "MultiPolygon") {
                    feature.geometry.coordinates.forEach(polygon => {
                        districtCenters[district].push(polygon[0].filter((_, i) => i % 10 === 0));
                    });
                }
            });
        } catch (error) {
            console.error(`Ошибка обработки ${district}:`, error);
            districtCenters[district] = [];
        }
    }
    console.log("districtCenters обновлён:", districtCenters);
}


function isPointInPolygon(point, polygon) {
    let [px, py] = point;
    let inside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        let [xi, yi] = polygon[i];
        let [xj, yj] = polygon[j];
        let intersect = ((yi > py) !== (yj > py)) && (px < (xj - xi) * (py - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

function getClosestDistrict() {
    const centerScreen = [
        (canvas.width / 2 - zoomTransform.x) / zoomTransform.k, 
        (canvas.height / 2 - zoomTransform.y) / zoomTransform.k
    ];
    const centerGeo = projection.invert(centerScreen);
    
    // Если карта не сильно сдвинулась, используем кеш
    if (lastDistrict && lastCenterGeo) {
        let dx = Math.abs(centerGeo[0] - lastCenterGeo[0]);
        let dy = Math.abs(centerGeo[1] - lastCenterGeo[1]);
        if (dx < 0.01 && dy < 0.01) {
            return lastDistrict;
        }
    }
    
    let closestDistrict = null;
    let minDistance = Infinity;
    let detailFactor = zoomTransform.k > 10 ? 1 : 2; 

    Object.entries(districtCenters).forEach(([district, borders]) => {
        let isInside = borders.some(border => isPointInPolygon(centerGeo, border));
        
        if (isInside) {
            closestDistrict = district;
            minDistance = 0;
            return;
        }
        
        borders.forEach(border => {
            let districtMinDistance = Math.min(...border.filter((_, i) => i % detailFactor === 0)
                .map(([lon, lat]) => d3.geoDistance(centerGeo, [lon, lat])));
            if (districtMinDistance < minDistance) {
                minDistance = districtMinDistance;
                closestDistrict = district;
            }
        });
    });
    
    lastDistrict = closestDistrict;
    lastCenterGeo = centerGeo;
    return closestDistrict;
}


async function render() {
    if (isRendering) return;
    isRendering = true;

    await new Promise(resolve => (window.requestIdleCallback || function(cb) { 
        setTimeout(() => cb({ timeRemaining: () => 50 }), 1); })(resolve));

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(zoomTransform.x, zoomTransform.y);
    ctx.scale(zoomTransform.k, zoomTransform.k);

    const visibleWidth = canvas.width / zoomTransform.k + 1000/zoomTransform.k;
    const visibleHeight = canvas.height / zoomTransform.k + 1000/zoomTransform.k;
    const visibleX = -zoomTransform.x / zoomTransform.k;
    const visibleY = -zoomTransform.y / zoomTransform.k;

    ctx.beginPath();
    ctx.rect(visibleX, visibleY, visibleWidth, visibleHeight);
    ctx.clip();

    if (mapData && zoomTransform.k < 30) {
        ctx.globalAlpha = mapData.opacity;
        mapData.data.features.forEach(feature => {
            ctx.beginPath();
            path(feature);
            ctx.fillStyle = mapData.fillColor;
            ctx.fill();
            ctx.strokeStyle = mapData.strokeColor;
            ctx.lineWidth = Math.max(22 / (zoomTransform.k * 10), 0.001);
            ctx.stroke();
        });
        canvas.style.backgroundColor = darkMode ? "#111" : "#eee";
    } else {
        canvas.style.backgroundColor = darkMode ? "#091329" : "#27543d";
    }

    if (zoomTransform.k > 10) {
        const currentDistrict = getClosestDistrict();

        // Подгружаем данные только при необходимости
        if (!districtData[currentDistrict]) {
            await loadDistrictMaps(currentDistrict, darkMode ? colorSchemeNight : colorSchemeDay);
        }

        const layers = districtData[currentDistrict] || [];

        for (const layer of layers) {
            if (!layer.quadtree) continue;

            ctx.globalAlpha = layer.opacity;
            const isWater = layer.strokeColor === colorSchemeDay["Water"][1] || layer.strokeColor === colorSchemeNight["Water"][1];
            const isRoad = layer.strokeColor === colorSchemeDay["Roads"][1] || layer.strokeColor === colorSchemeNight["Roads"][1];
            const alwaysVisible = layer.strokeColor === colorSchemeDay["Borders"][1] || layer.strokeColor === colorSchemeNight["Borders"][1] ||
                      layer.fillColor === colorSchemeDay["Places"][0] || layer.fillColor === colorSchemeNight["Places"][0];
            layer.quadtree.visit((node, x0, y0, x1, y1) => {
                if (!alwaysVisible && (x1 < visibleX || x0 > visibleX + visibleWidth || y1 < visibleY || y0 > visibleY + visibleHeight)) {
                    return true;
                }
                
                if (!node.length && node.data) {
                    const feature = node.data;

                    ctx.beginPath();
                    path(feature);
                    
                    const maxSpeed = feature.properties.maxspeed || 0;
                    const highSpeedRoad = maxSpeed >= 21;
                    const lowSpeedRoad = maxSpeed < 20;

                    let lineWidth = isWater
                        ? Math.max((feature.properties.width + 1) / zoomTransform.k, 0.0005)
                        : isRoad
                            ? Math.max(((maxSpeed / 20) + 1) / (zoomTransform.k + 4), 0.0002)
                            : Math.max(layer.lineWidth / (zoomTransform.k + 5), 0.0002);

                    ctx.lineWidth = lineWidth;
                    ctx.strokeStyle = layer.strokeColor;

                    const showLine =
                        (isWater || isRoad) && (lineWidth <= 0.005 || feature.properties.width > 5 && zoomTransform.k > 50) ||
                        isRoad && (lowSpeedRoad && zoomTransform.k > 250 || highSpeedRoad && zoomTransform.k > 50);

                    if (showLine) {
                        ctx.stroke();
                        if (feature.properties.name && zoomTransform.k > 700) {
                            addRiverLabel(feature);
                        }
                    }

                    

                    if (layer.fillColor !== "none"){
                        ctx.stroke();
                        ctx.fillStyle = layer.fillColor;
                        ctx.fill();
                    }

                    if (layer.fillColor === "none" && !isWater && !isRoad) {
                        ctx.stroke();
                    }
                }
            });
        }
    }

    // Подсветка
    if (hoveredFeature) {
        ctx.globalAlpha = 1;
        const bbox = path.bounds(hoveredFeature);
        const centerX = (bbox[0][0] + bbox[1][0]) / 2;
        const centerY = (bbox[0][1] + bbox[1][1]) / 2;

        const gradient = ctx.createRadialGradient(
            centerX, centerY, 0, centerX, centerY,
            Math.max(bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1]) * zoomTransform.k
        );

        gradient.addColorStop(0.7, darkMode ? "#000" : "#EDC5AB");
        gradient.addColorStop(0, darkMode ? "#060826" : "#E7EAEF");

        if (zoomTransform.k < 10) {
            for (let i = 5; i > 0; i--) {
                ctx.globalAlpha = 1 / i;
                ctx.beginPath();
                path(hoveredFeature);
                ctx.lineWidth = 2 + i - zoomTransform.k / 10;
                ctx.strokeStyle = darkMode
                    ? `rgba(232, 171, 85, ${1 - i / 5})`
                    : `rgba(18, 47, 71, ${i / 5})`;
                ctx.stroke();
            }
            ctx.globalAlpha = Math.max(1 - zoomTransform.k / 10, 0);
        }

        if ((zoomTransform.k >= 10 && zoomTransform.k <= 11) || (zoomTransform.k >= 50 && zoomTransform.k <= 150)) {
            hoveredFeature = null;
            tooltip.style.display = "none";
        }

        ctx.fillStyle = gradient;
        ctx.beginPath();
        path(hoveredFeature);
        ctx.fill();

        if (zoomTransform.k > 11) {
            ctx.fillStyle = darkMode && zoomTransform.k > 100 ? "#53576e" : "#ffdfdd";
            ctx.fill();
            ctx.lineWidth = zoomTransform.k < 100 ? 0.045 : 0.0015;
            ctx.strokeStyle = darkMode
                ? (zoomTransform.k <= 100 ? "rgba(232, 171, 85, 0.9)" : "#aaa")
                : "rgba(13, 15, 11, 0.76)";
            ctx.stroke();
        }
    }

    ctx.restore();
    isRendering = false;
}

function addRiverLabel(feature) {
    ctx.save();
    ctx.fillStyle = darkMode ? "#ccc" : "#FFFAF4";
    ctx.shadowOffsetX = 2;        // Горизонтальное смещение тени
    ctx.shadowOffsetY = 2;        // Вертикальное смещение тени
    ctx.shadowBlur = 1;           // Размытие тени
    ctx.shadowColor = "rgba(0, 0, 0, 0.5)"; 
    ctx.font = `0.001em Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    let centroid = path.centroid(feature); // Определяем центр реки
    if (!centroid || centroid.length < 2) return;

    let coords = feature.geometry.coordinates;
    if (feature.geometry.type === "MultiLineString") {
        coords = coords[0]; // Берём первую линию в MultiLineString
    }

    if (coords.length < 2) return; // Проверяем, есть ли хотя бы две точки
    
    let midIndex = Math.floor(coords.length / 2);

    if(midIndex - 1 > 0 && midIndex + 1 <= coords.length){
        let [x1, y1] = projection(coords[midIndex - 1]);
        let [x2, y2] = projection(coords[midIndex]);
        let [x3, y3] = projection(coords[midIndex + 1]);
        let angle1 = Math.atan2(y2 - y1, x2 - x1);
        let angle2 = Math.atan2(y3 - y2, x3 - x2);
        let avgAngle = (angle1 + angle2) / 2;

        if (avgAngle > 80 || avgAngle < -80) {
            avgAngle += 180;
        }
        ctx.translate(centroid[0], centroid[1]); 
        ctx.rotate(avgAngle * (Math.PI / 180));
    }
    else {
        
        let [x1, y1] = projection(coords[0]);
        let [x2, y2] = projection(coords[1]);
        let angle = Math.atan2(y2 - y1, x2 - x1); // Угол наклона
        ctx.translate(centroid[0], centroid[1]); // Перемещаем в центр
        ctx.rotate(angle);
        if (angle > 90 || angle < -90) {
            angle += 180;
        }
    }
    ctx.fillText(feature.properties.name, 0, 0);
    ctx.restore();
}



function capitalizeFirstLetter(str) {
    if (!str || typeof str !== "string") return "Нет данных";
    return str.charAt(0).toUpperCase() + str.slice(1);
}

canvas.addEventListener("mousemove", (event) => {
    const { offsetX, offsetY } = event;
    const mousePos = projection.invert([(offsetX - zoomTransform.x) / zoomTransform.k, (offsetY - zoomTransform.y) / zoomTransform.k]);
    let foundFeature = null;
    document.body.style.cursor = loader.style.display == "none" ? "default" : "progress";

    if (zoomTransform.k < 10 && loader.style.display == "none"){
        mapData.data.features.forEach(feature => {
            if (d3.geoContains(feature.geometry, mousePos)) {
                foundFeature = feature;
                document.body.style.cursor = "pointer";
            }
        });
    }

    if (zoomTransform.k > 10) {
        const currentDistrict = getClosestDistrict();
        
        if (districtData[currentDistrict]) {
            districtData[currentDistrict].forEach(layer => {
                if (zoomTransform.k < 100 && layer.data && layer.data.features && (layer.fillColor === colorSchemeDay["Places"][0] || layer.fillColor === colorSchemeNight["Places"][0])) { 
                    layer.data.features.forEach(feature => {
                        if (d3.geoContains(feature.geometry, mousePos)) {
                            foundFeature = feature;
                            document.body.style.cursor = "pointer";
                        }
                    });
                }
                if (zoomTransform.k > 1000 && layer.data && layer.data.features && (layer.fillColor === colorSchemeDay["Buildings"][0] || layer.fillColor === colorSchemeNight["Buildings"][0]) || (layer.fillColor === colorSchemeDay["Church"][0] || layer.fillColor === colorSchemeNight["Church"][0]) || (layer.fillColor === colorSchemeDay["GreenPlaces"][0] || layer.fillColor === colorSchemeNight["GreenPlaces"][0]) || (layer.fillColor === colorSchemeDay["Terminals"][0] || layer.fillColor === colorSchemeNight["Terminals"][0]) ) { 
                    layer.data.features.forEach(feature => {
                        if (d3.geoContains(feature.geometry, mousePos)) {
                            foundFeature = feature;
                            document.body.style.cursor = "pointer";
                        }
                    });
                }
            });
        }
    }
    
    hoveredFeature = foundFeature;
    render();

    if (hoveredFeature) {
        tooltip.style.left = `${event.pageX + 20}px`;
        tooltip.style.top = `${event.pageY - 20}px`;
        if (zoomTransform.k <= 10){
            tooltip.textContent = capitalizeFirstLetter(hoveredFeature.properties.Name);
            }
        else {
            tooltip.textContent = capitalizeFirstLetter(hoveredFeature.properties.name)
        }
        tooltip.style.display = "block";
    } else {
        tooltip.style.display = "none";
        
    }
});

async function fetchWikiData(wikidataID) {
    infoBox.innerHTML = `
    <div style="position: relative; padding: 10px;">
    ${closeButton}
    <div style="padding: 20px; text-align: center;">
        <strong>Загрузка данных...</strong>
    </div>
    </div>
    `;
    infoBox.style.display = "block";
    
    let url = `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=${wikidataID}&format=json&origin=*`;

    try {
        
        let response = await fetch(url);
        let data = await response.json();
        if (data.entities && data.entities[wikidataID]) {
            let entity = data.entities[wikidataID];
            updateInfoBoxWiki(entity, wikidataID);
        } 
        
        else {
            closeInfoBox();
        }
    } catch (error) {
        closeInfoBox();
    }
}

async function fetchWikiIDfromOSM(osmID) {
    console.log("Запрашиваем Wikidata ID для OSM ID:", osmID);

    let query = `
        [out:json];
        (
            node(${osmID});
            way(${osmID});
            relation(${osmID});
        );
        out body;
    `;

    let url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

    try {
        let response = await fetch(url);
        let data = await response.json();

        for (let element of data.elements) {
            if (element.tags && element.tags["wikidata"]) {
                let wikidataID = element.tags["wikidata"];
                fetchWikiData(wikidataID);
                return;
            }
        }


    } catch (error) {
        closeInfoBox();
    }
}




async function fetchEntityLabel(entityID) {
    if (!entityID) return null;
    let url = `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=${entityID}&format=json&origin=*`;

    try {
        let response = await fetch(url);
        let data = await response.json();
        if (data.entities && data.entities[entityID] && data.entities[entityID].labels) {
            let labels = data.entities[entityID].labels;
            return labels.ru ? labels.ru.value : labels.en ? labels.en.value : null;
        }
    } catch (error) {
        console.error("Ошибка загрузки данных с Wikidata:", error);
    }
    return null;
}


// Глобальные переменные
let regionsData = null;
let availableMetrics = new Set();
let currentTitle = '';
let currentFileName = '';
let socialToggle = '';
let availableFilesForRegion = [];

async function getAvailableFiles() {
    try {
        
        const mockFiles = [
        "Образование", "Жильё", "Платные_услуги_населению", "Население",
        "Охрана_окружающей_среды", "Коллективные_средства_размещения", 
        "Организация_охраны_общественного_порядка", "Муниципальная_собственность",
        "Финансовая_деятельность", "Жилые_Помещения", "Бюджет",
        "Почтовая_и_телефонная_связь", "Сельское_хозяйство", 
        "Занятость_и_зарплата", "Культура", "Спорт", "Территория"
        ];

        if (availableFilesForRegion.length > 0) {
            return availableFilesForRegion;
        }

        return mockFiles;
        
    } catch (error) {
        console.error('Ошибка получения файлов:', error);
        return [];
    }
}

async function findFilesContainingRegionName(regionName) {
    availableFilesForRegion = [];

    const files = await getAvailableFiles(); // все mock-файлы
    
    for (const file of files) {
        const filePath = `data/sorted/${file}.json`;
        try {
            const response = await fetch(filePath);
            if (!response.ok) continue;

            const data = await response.json();

            // ❗️временная подмена глобального regionsData
            const oldRegionsData = regionsData;
            regionsData = data;

            const regionData = findRegionData(regionName);

            // ❗️если данные найдены — файл подходит
            if (regionData) {
                if (!availableFilesForRegion.includes(file)) {
                    availableFilesForRegion.push(file);
                }
            }

            regionsData = oldRegionsData; // восстановить
        } catch (err) {
            console.error(`Ошибка чтения файла ${filePath}:`, err);
        }
    }
}


async function showFileListInSocialTab() {
    const socialContent = document.getElementById('socialContent');
    socialContent.innerHTML = '<div>Загрузка списка файлов...</div>';

    try {
        
        const files = availableFilesForRegion.length > 0 ? availableFilesForRegion : [];

        if (files.length === 0) {
            socialContent.innerHTML = `
                <div>Нет данных для <strong>${currentTitle}</strong></div>
            `;
        } else {
            socialContent.innerHTML = `
                <h3>Доступные показатели для <strong>${currentTitle}</strong></h3>
                <div class="file-list">
                    ${files.map(file => `
                        <div class="file-item" data-file="${file}">
                            ${file.replace(/_/g, ' ')}
                        </div>
                    `).join('')}
                </div>
            `;
        }

        document.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', async () => {
                currentFileName = item.getAttribute('data-file');
                const cleanTitle = currentFileName.replace(/_/g, ' ');

                const titleElement = document.querySelector('.social-tab-header h2');
                if (titleElement) {
                    titleElement.textContent = cleanTitle;
                }

                if (await loadRegionsData()) {
                    if (currentTitle) {
                        showSocialIndicators(currentTitle);
                    } else {
                        socialContent.innerHTML = '<div>Данные загружены. Выберите регион на карте.</div>';
                    }
                } else {
                    socialContent.innerHTML = '<div class="error">Ошибка загрузки файла</div>';
                }
            });
        });

    } catch (error) {
        socialContent.innerHTML = `<div class="error">Ошибка: ${error.message}</div>`;
    }
}

async function loadRegionsData() {
    if (!currentFileName) return false;
    
    try {
        const response = await fetch(`data/sorted/${currentFileName}.json`);
        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
        
        regionsData = await response.json();
        availableMetrics = new Set();
        
        // Собираем все уникальные показатели
        Object.values(regionsData).forEach(region => {
            Object.values(region).forEach(yearData => {
                Object.keys(yearData).forEach(metric => {
                    availableMetrics.add(metric);
                });
            });
        });
        
        console.log(`Данные загружены из ${currentFileName}`);
        return true;
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        return false;
    }
}

// Функция нормализации названий регионов
const normalizeRegionName = (name) => {
    return name.toLowerCase()
        .replace(/ё/g, 'е')
        .replace(/[^а-я\s-]/gi, '')
        .replace(/\s+/g, ' ')
        .trim();
};

// Функция поиска данных по региону
function findRegionData(regionName) {
    if (!regionsData) return null;
    
    const normalizedSearchName = normalizeRegionName(regionName);
    
    const specialCases = {
        'усть-цилемский': ['Муниципальный район Усть-Цилемский'],
        'сыктывкар': ['Городской округ Сыктывкар'],
        'ухта': ['Муниципальный округ Ухта','Городской округ Ухта'],
        'инта': ['Муниципальный округ Инта','Городской округ Инта'],
        'воркута': ['Муниципальный округ Воркута','Городской округ Воркута'],
        'вуктыл': ['Муниципальный округ Вуктыл','Муниципальный район Вуктыл','Городской округ Вуктыл'],
        'койгородский' : ['Муниципальный район Койгородский']
    };

    // Проверка специальных случаев
    for (const [key, possibleNames] of Object.entries(specialCases)) {
        if (normalizedSearchName.includes(key)) {
            // Ищем первое существующее название из возможных вариантов
            for (const name of possibleNames) {
                if (regionsData[name]) {
                    return regionsData[name];
                }
            }
            return null; // если ни один вариант не найден
        }
    }

    // Стандартный поиск по всем регионам
    for (const [fullName, data] of Object.entries(regionsData)) {
        const normalizedFullName = normalizeRegionName(
            fullName.replace(/Городской округ|Муниципальный район|Муниципальный округ|Город|МО/gi, '')
        );
        
        if (normalizedFullName.includes(normalizedSearchName) || 
            normalizedSearchName.includes(normalizedFullName)) {
            return data;
        }
    }

    return null;
}

// Цвета для графиков в светлой теме 
const chartColorsLight = [
    '#1EBC61', // зелёный
    '#D08821', // золотистый
    '#5092DC', // голубой
    '#C0392B', // бордовый
    '#B9C900', // оливковый
    '#48C9B0', // морская волна
    '#779985', // глубокий зелёный
    '#9FAEE2', // лавандовый
    '#ABBD97', // светлый оливковый
    '#F39C12', // оранжево-жёлтый
    '#BB8FCE', // сиреневый
    '#E74C3C'  // красный
];

const chartColorsDark = [
    '#F5A623', // золотисто-оранжевый
    '#8A94E3', // лавандовый
    '#3498DB', // голубой
    '#F0B45C', // светло-золотистый
    '#5DA7C0', // морская волна
    '#7A7FDB', // светло-лавандовый
    '#C26B5E', // кирпичный
    '#27AE60', // зелёный
    '#E74C3C', // красный
    '#AF7AC5', // фиолетовый
    '#F39C12', // оранжево-жёлтый
    '#1ABC9C'  // бирюзовый
];

function getChartColors() {
    return darkMode ? chartColorsDark : chartColorsLight;
}

async function showSocialIndicators(regionName) {
    const socialContent = document.getElementById('socialContent');
    const backButton = document.getElementById('backButton');
    const titleElement = document.querySelector('.social-tab-header h2');
    if (titleElement) {
      titleElement.textContent = `${currentFileName.replace(/_/g, ' ')}`;
    }
    backButton.style.visibility = 'visible';
    socialContent.innerHTML = '<div>Загрузка данных...</div>';
    
    try {
        if (!regionsData && !await loadRegionsData()) {
            throw new Error('Не удалось загрузить данные регионов');
        }
        const regionData = findRegionData(regionName);
    
        if (regionData) {
            const years = Object.keys(regionData).sort((a, b) => parseInt(a) - parseInt(b));
            const metrics = Array.from(availableMetrics);
    
            // Фильтруем показатели и годы с данными
            const metricsWithData = metrics.filter(metric => {
                return years.some(year => regionData[year][metric] !== undefined);
            });
    
            // Для каждого показателя находим годы с данными
            const metricYears = {};
            metricsWithData.forEach(metric => {
                metricYears[metric] = years.filter(year => regionData[year][metric] !== undefined);
            });
    
            // Основная разметка
            socialContent.innerHTML = `
                <div id="dataTable" class="tab-content active">
                    <h3>${regionName}</h3>
                    <div class="table-scroll-wrapper">
                        <table class="compact-table">
                            <thead>
                                <tr>
                                    <th>Год</th>
                                    ${metrics.map(metric => `<th>${metric}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${years.map(year => `
                                    <tr>
                                        <td>${year}</td>
                                        ${metrics.map(metric => `
                                            <td>${regionData[year][metric] !== undefined ? regionData[year][metric] : '-'}</td>
                                        `).join('')}
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                </div>
            
                ${metricsWithData.length > 0 ? `
                <div id="dataCharts" class="tab-content">
                    <h3>Графики показателей</h3>
                    <div class="charts-container">
                        ${metricsWithData.map((metric, index) => {

                           return `
                            <div class="chart-wrapper">
                                <h4>${metric}</h4>
                                <div class="chart-inner">
                                    <canvas id="chart_${index}" height="200"></canvas>
                                </div>
                            </div>
                            `;
                        }).join('')}
                    </div>
                </div>
                ` : ''}
            `;

        metricsWithData.forEach((metric, index) => {
            const ctx = document.getElementById(`chart_${index}`);
            if (!ctx) return;
            
            const availableYears = metricYears[metric];
            const dataValues = availableYears.map(year => regionData[year][metric]);
            if (dataValues.every(val => val === null || val === undefined)) {
                console.warn(`Нет данных для показателя: ${metric}`);
                return;
              }
            Chart.register({
              id: 'background',
              beforeDraw: (chart) => {
                const { ctx, width, height } = chart;
                ctx.save();
                ctx.fillStyle = 'rgba(55, 55, 55, 0.15)'; // тёмный фон
                ctx.fillRect(0, 0, width, height);
                ctx.restore();
              }
            });
            new Chart(ctx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: availableYears,
                    datasets: [{
                        label: metric,
                        data: dataValues,
                        borderColor: `${getChartColors()[index % getChartColors().length]}80`,
                        backgroundColor: `${getChartColors()[index % getChartColors().length]}40`,
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 12,
                        tension: 0.1,
                       
                        fill: true
                    }]
                },
                options: {
                    animation: {
                        duration: 2000,
                        easing: 'easeOutQuart',
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#333',
                            
                            callbacks: {
                                label: (context) => context.raw
                            }
                        },
                        background: {
                            color: '#ffa' // тёмный фон внутри canvas
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                        },
                        y: {
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            // Автоматическое определение границ
                            beginAtZero: false,
                            min: Math.floor(Math.min(...dataValues)) > 0 
                            ? Math.floor(Math.min(...dataValues) * 0.5 - 0.00001 ) 
                            : Math.floor(Math.min(...dataValues) * 1.5 - 0.00001 ),
                            max: Math.ceil(Math.max(...dataValues)) >= 0
                            ? Math.ceil((Math.max(...dataValues) * 1.5 + 0.00001) )
                            : Math.ceil((Math.max(...dataValues) * 0.5 + 0.00001) )
                        }
                    }
                }
            });
        });
            

            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    
                    btn.classList.add('active');
                    document.getElementById(btn.dataset.tab).classList.add('active');
                });
            });
            
        } else {
            socialContent.innerHTML = `<p class="error-message">Данные для региона "${regionName}" не найдены</p>`;
        }
        const header = document.querySelector('.social-tab-header');
        const scrollContainer = document.getElementById('socialTab');
        
        scrollContainer.addEventListener('scroll', () => {
            const isScrolling = scrollContainer.scrollTop > 3;
            header.style.backdropFilter = isScrolling ? 'blur(2px)' : 'none';

            header.style.webkitBackdropFilter = isScrolling ? 'blur(1px)' : 'none';
        })

    } catch (error) {
        console.error('Ошибка:', error);
        socialContent.innerHTML = `
            <p class="error-message">Ошибка загрузки данных</p>
            <p>${error.message}</p>
        `;
    }
}

let closeButton = `
        <div class="close-btn", style="position: absolute; top: -15px; right: -5px; border-radius: 50%; padding: 5px;" onclick="closeInfoBox()">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="black" d="M6 6L18 18M6 18L18 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
        </div>`;

async function updateInfoBoxWiki(entity, wikidataID) {

    
    let labels = entity.labels || {};
    const clickedTitle = capitalizeFirstLetter(hoveredFeature.properties.Name);
    if (clickedTitle && clickedTitle !== "Нет данных") {
        currentTitle = clickedTitle;
    }
    let sitelinks = entity.sitelinks || {};
    let claims = entity.claims || {};

    let title = labels.ru ? labels.ru.value : labels.en ? labels.en.value : "Неизвестное место";
    let wikipediaURL = sitelinks.ruwiki ? sitelinks.ruwiki.url : sitelinks.enwiki ? sitelinks.enwiki.url : null;

    // Дополнительные данные (остается без изменений)
    let instanceOfID = claims.P31 ? claims.P31[0].mainsnak.datavalue.value.id : null;
    let capitalOfID = claims.P1376 ? claims.P1376[0].mainsnak.datavalue.value.id : null;
    let postalCode = claims.P281 ? claims.P281[0].mainsnak.datavalue.value : null;
    let population = claims.P1082 ? parseInt(claims.P1082[0].mainsnak.datavalue.value.amount) + " человек" : null;
    let area = claims.P2046 ? parseFloat(claims.P2046[0].mainsnak.datavalue.value.amount) + " км²" : null;
    let elevation = claims.P2044 ? parseFloat(claims.P2044[0].mainsnak.datavalue.value.amount) + " м" : null;
    let inceptionDate = claims.P571 ? new Date(claims.P571[0].mainsnak.datavalue.value.time).getFullYear() : null;

    // Координаты и изображения (остается без изменений)
    let coordinates = claims.P625 ? claims.P625[0].mainsnak.datavalue.value : null;
    let latLon = coordinates ? `${coordinates.latitude.toFixed(4)}, ${coordinates.longitude.toFixed(4)}` : null;
    let imageFile = claims.P18 ? claims.P18[0].mainsnak.datavalue.value : null;
    let imageUrl = imageFile ? `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(imageFile)}` : null;
    let flag = claims.P41 ? `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(claims.P41[0].mainsnak.datavalue.value)}` : null;
    let coatOfArms = claims.P94 ? `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(claims.P94[0].mainsnak.datavalue.value)}` : null;

    // Получаем названия "instance of" и "capital of"
    let instanceOfTitle = instanceOfID ? await fetchEntityLabel(instanceOfID) : null;
    let capitalOfTitle = capitalOfID ? await fetchEntityLabel(capitalOfID) : null;

    
    

        
    // Создаем основное содержимое
    mainContent = `
        <div style="position: relative; padding: 10px;">
            <div id="showSocialButton", style="position: absolute; top: -12px; left: 0px; cursor: pointer; background: none; border-radius: 50%; padding: 5px;"">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="18" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-opacity="1">
                    <path style="fill:none;" d="M1.7,1.1V21.65H22" />
                    <path style="fill:none;" d="M1.7,21.56L5.76,10.94L9.59,17.28L12.74,6.89L17.36,13.9L21.67,1.23" />
                </svg>
            </div>
            <br>
            ${closeButton}
            <h1>${title}</h1>
            ${instanceOfTitle ? `<strong>Тип:</strong> ${instanceOfTitle}<br>` : ''}
            ${capitalOfTitle ? `<strong>Столица:</strong> ${capitalOfTitle}<br>` : ''}
            ${postalCode ? `<strong>Почтовый индекс:</strong> ${postalCode}<br>` : ''}
            ${population ? `<strong>Население:</strong> ${population}<br>` : ''}
            ${area ? `<strong>Площадь:</strong> ${area}<br>` : ''}
            ${elevation ? `<strong>Высота над ур. моря:</strong> ${elevation}<br>` : ''}
            ${inceptionDate ? `<strong>Дата основания:</strong> ${inceptionDate}<br>` : ''}
            ${latLon ? `<strong>Координаты:</strong> ${latLon}<br>` : ''}
            ${wikipediaURL ? `<a href="${wikipediaURL}" target="_blank">Читать в Википедии</a><br>` : ''}
            ${flag ? `<strong>Флаг:</strong><br> <img src="${flag}" alt="Флаг" style="max-width: 100px; margin-top: 10px;"><br>` : ''}
            ${coatOfArms ? `<strong>Герб:</strong><br> <img src="${coatOfArms}" alt="Герб" style="max-width: 100px; border: none; margin-top: 10px;"><br>` : ''}
            ${imageUrl ? `<img src="${imageUrl}" alt="${title}" style="max-width: 100%; margin-top: 10px;"><br>` : ''}
            <strong>Wikidata ID:</strong> <a href="https://www.wikidata.org/wiki/${wikidataID}" target="_blank">${wikidataID}</a>
        </div>`;

    infoBox.innerHTML = mainContent;
    infoBox.style.display = "block";

    
    

    // Инициализация социальной вкладки (если еще не создана)
    let socialTab = document.getElementById('socialTab');
    if (!socialTab) {
        socialTab = document.createElement('div');
        socialTab.id = 'socialTab';
        
        socialTab.innerHTML = `
        <div class="social-tab-header">
          <div id="backButton" style="cursor: pointer; visibility: hidden;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
          </div>
          <h2 style="margin: 0">Социальные показатели</h2>
          <div class="close-btn" onclick="toggleSocialButton()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
          </>
        </div>
        <div class="social-tab-content" id="socialContent"></div>
      `;
        document.body.appendChild(socialTab);
    }
    if (!currentFileName) {
        showFileListInSocialTab();
    }

  

    

     // Обработчик кнопки "Назад"
     document.getElementById('backButton')?.addEventListener('click', async () => {
        currentFileName = '';
        availableFilesForRegion = [];
        
        if (currentTitle) {
            await findFilesContainingRegionName(currentTitle);
        }

        const titleElement = document.querySelector('.social-tab-header h2');
        if (titleElement) {
          titleElement.textContent = 'Социальные показатели'; // Возвращаем исходный заголовок
        }
        document.getElementById('backButton').style.visibility = 'hidden';
        showFileListInSocialTab();
    });

    // Обработчик для кнопки показателей
    document.getElementById('showSocialButton')?.addEventListener('click', () => {
        toggleSocialButton();
        if (socialToggle) {
            if (!currentFileName) {
                showFileListInSocialTab();
            } else if (currentTitle) {
                showSocialIndicators(currentTitle);
            }
        }
    });
}




function toggleSocialButton(){
    const socialTab = document.getElementById('socialTab');
    const b = document.getElementById('showSocialButton');
    socialToggle = !socialToggle;
    socialTab.style.display = socialToggle ? 'block' : 'none';
    b.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="18" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-opacity="1">
                    <path d="M1.7,1.1V21.65H22" />
                    <path d="M1.7,21.56L5.76,10.94L9.59,17.28L12.74,6.89L17.36,13.9L21.67,1.23" />
                    ${socialToggle ? `<path d="M1.43,22.66L22.62,1.36" stroke="#6d0000" stroke-width="4" /><path d="M22.62,1.36L1.43,22.66" transform="matrix(-1 0 0 1 24.05 0)" stroke="#6d0000" stroke-width="4" />`: ''}
                </svg>`
}



canvas.addEventListener("click", async () => {
    document.body.style.cursor = "grab";
    if (hoveredFeature) {
        if (zoomTransform.k <= 11) {
        currentTitle = capitalizeFirstLetter(hoveredFeature.properties.Name);
        } else {
        currentTitle = capitalizeFirstLetter(hoveredFeature.properties.name);
        }
        let wikidataID = hoveredFeature.properties.wikidata || hoveredFeature.properties.wikidata_2;

        if (wikidataID && zoomTransform.k <= 11) {
            // console.log("Wikidata ID:", wikidataID);
            fetchWikiData(wikidataID);
        } 
        
        if (zoomTransform.k > 11) {
            let osmID = hoveredFeature.properties.osm_id;
            if (osmID) {
                fetchWikiIDfromOSM(osmID);
            }
        }
        
        
        if (!currentFileName) {
            await findFilesContainingRegionName(currentTitle);
            showFileListInSocialTab();
        }
        else if (currentTitle) {
            showSocialIndicators(currentTitle);
        }
    
        
    } else {
        // Если клик в пустое место — скрываем инфобокс
        closeInfoBox();
    }
});

function closeInfoBox() {
    infoBox.style.display = "none";
}



const zoom = d3.zoom()
    .scaleExtent([1, 10000])
    .on("zoom", (event) => {
        const prevZoom = zoomTransform.k;
        zoomTransform = event.transform;
        
        // Проверяем переход через границы 300 и 800
        const buildingsBoundaryCrossed = 
            (prevZoom <= 800 && zoomTransform.k > 800) || 
            (prevZoom > 800 && zoomTransform.k <= 800);
            
        const greenPlacesBoundaryCrossed =
            (prevZoom <= 300 && zoomTransform.k > 300) ||
            (prevZoom > 300 && zoomTransform.k <= 300);
        
        if (buildingsBoundaryCrossed || greenPlacesBoundaryCrossed) {
            Object.keys(cachedData).forEach(key => {
                if ((key.endsWith("Buildings") && buildingsBoundaryCrossed) ||
                    (key.endsWith("GreenPlaces") && key.endsWith("Parking") && greenPlacesBoundaryCrossed)) {
                    delete cachedData[key];
                }
            });
            // Перезагружаем текущий район
            const district = getClosestDistrict();
            loadDistrictMaps(district, darkMode ? colorSchemeNight : colorSchemeDay);
        }
        
        render();
    });
        //console.log(zoomTransform.k);

d3.select(canvas).call(zoom);

window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    updateProjection();
    render();
});

function clearMap() {
    districtData = {};
}

changeIconColor();
createMapControls(mapType);
showLoader("none")

// Вызываем обновление данных
updateDistrictCenters();


drawMap("map/GeoJSON/Komi.geojson", "#37745B", "#8B9D77", 1);