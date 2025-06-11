<<<<<<< HEAD
// static/js/popover.js - Multi-modal with classic "tall card" style and layout

import { MODEL_LOGOS_SVG, PROVIDER_LOGOS_SELECTOR, CAPABILITY_ICONS, PREMIUM_ICONS_BADGES } from './config.js';

let modelsData = null;
let isPopoverExpandedView = false;
let openProviderSections = {};
let currentMediaType = 'llm'; // Default media type

// --- Popover UI and State ---

export function toggleModelPopover() {
    const popover = document.getElementById('modelDropdown');
    const overlay = document.getElementById('modelDropdownOverlay');
    const selector = document.querySelector('.model-selector');
    const isOpen = popover.classList.toggle('active');
    overlay.classList.toggle('active', isOpen);
    selector.classList.toggle('active', isOpen);

    if (isOpen) {
        if (!modelsData) {
            initializeModels();
        }
        document.getElementById('modelSearchInput').focus();
    }
}

export function togglePopoverExpandedView(event) {
    if (event) event.stopPropagation();
    isPopoverExpandedView = !isPopoverExpandedView;
    renderModelPopoverContent();

    const btn = document.getElementById('popoverShowMoreBtn');
    const btnText = btn.querySelector('span');
    const btnIcon = btn.querySelector('svg.show-more-less-icon');

    if (isPopoverExpandedView) {
        btnText.textContent = 'Show less';
        btnIcon.innerHTML = `<path d="m18 15-6-6-6 6"></path>`;
    } else {
        btnText.textContent = 'Show all providers';
        btnIcon.innerHTML = `<path d="m6 9 6 6 6-6"></path>`;
    }
}

// --- Model Data and Rendering ---

async function initializeModels() {
    try {
        const response = await fetch('/models/categorized');
        if (!response.ok) throw new Error('Failed to fetch models');
        modelsData = await response.json();
        console.log('Loaded categorized models data:', modelsData);
        renderModelPopoverContent();
    } catch (error) {
        console.error('Error loading models:', error);
        const popoverContent = document.getElementById('popoverScrollableContent');
        if (popoverContent) {
            popoverContent.innerHTML = '<p style="padding: 20px; text-align: center; color: var(--text-secondary);">Could not load models. Please check your database connection.</p>';
        }
    }
}

function renderModelPopoverContent() {
    if (!modelsData) return;

    const popoverContent = document.getElementById('popoverScrollableContent');
    popoverContent.innerHTML = '';

    const categories = {
        llm: { data: modelsData.llm_models || [], title: 'Text Models' },
        image: { data: modelsData.image_models || [], title: 'Image Models' },
        audio: { data: modelsData.audio_models || [], title: 'Audio Models' },
        video: { data: modelsData.video_models || [], title: 'Video Models' }
    };

    for (const type in categories) {
        const category = categories[type];
        const section = document.createElement('div');
        section.className = `media-section ${type === currentMediaType ? 'active' : ''}`;
        section.id = `${type}-section`;
        
        if (category.data.length > 0) {
            section.innerHTML = (type === 'llm') 
                ? renderClassicLlmsSection(category.data)
                : renderGenericModelsSection(category.data, type, category.title);
        } else {
            section.innerHTML = `<p style="text-align:center; padding: 40px 20px; color: var(--text-secondary);">No ${category.title.toLowerCase()} available.</p>`;
        }
        popoverContent.appendChild(section);
    }

    addPopoverCardClickListeners();
    addProviderToggleListeners();
}

function renderClassicLlmsSection(llmModels) {
    let html = '';
    
    const upgradeBannerHTML = `
        <div class="upgrade-banner-popover">
            <h3>Unlock all models + higher limits</h3>
            <div class="upgrade-content">
                <div class="price"><span class="amount">$8</span><span class="period">/month</span></div>
                <button class="upgrade-btn">Upgrade now</button>
            </div>
        </div>
    `;
    html += upgradeBannerHTML;
    
    const popularModels = llmModels.filter(m => m.premium || ['Claude Sonnet 4', 'Gemini 2.5 Flash', 'gpt-4o', 'o1-mini', 'DeepSeek-R1', 'Llama 4 Scout'].some(p => m.model_name.includes(p))).slice(0, 12);

    if (popularModels.length > 0) {
        html += `
            <div class="popover-model-section">
                <div class="popover-section-header">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                    Favorites
                </div>
                <div class="popover-model-grid">
                    ${popularModels.map(m => createClassicPopoverCard(m, 'llm')).join('')}
                </div>
            </div>`;
    }

    if (isPopoverExpandedView) {
        const modelsByProvider = llmModels.reduce((acc, model) => {
            (acc[model.provider_name] = acc[model.provider_name] || []).push(model);
            return acc;
        }, {});

        const providerOrder = ['Anthropic', 'Google', 'OpenAI', 'DeepSeek', 'Meta', 'xAI'];
        const sortedProviders = Object.keys(modelsByProvider).sort((a, b) => {
            const aIndex = providerOrder.indexOf(a); const bIndex = providerOrder.indexOf(b);
            if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
            if (aIndex !== -1) return -1; if (bIndex !== -1) return 1;
            return a.localeCompare(b);
        });
        
        html += `<div class="popover-section-header" style="margin: 20px 10px 10px 10px;">All Providers</div>`;

        for (const providerName of sortedProviders) {
            const providerModels = modelsByProvider[providerName];
            const providerKey = providerModels[0].provider;
            const isSectionOpen = openProviderSections[providerName] || false;
            let providerLogoHtml = (PROVIDER_LOGOS_SELECTOR[providerKey] || '').replace('class="model-logo"', 'class="model-logo-provider-header"');

            html += `
                <div class="provider-section-collapsible" style="padding: 0 10px;">
                    <div class="provider-section-header ${isSectionOpen ? 'open' : ''}" data-provider="${providerName}">
                        ${providerLogoHtml || `<span class="provider-logo-placeholder-header">${providerName.charAt(0).toUpperCase()}</span>`}
                        <span class="provider-name">${providerName}</span>
                        <span class="provider-model-count">(${providerModels.length})</span>
                        <svg class="provider-toggle-icon" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>
                    </div>
                    <div class="popover-model-grid provider-grid ${!isSectionOpen ? 'collapsed' : ''}">
                        ${providerModels.map(m => createClassicPopoverCard(m, 'llm')).join('')}
                    </div>
                </div>`;
        }
    }
    return html;
}

function renderGenericModelsSection(models, type, title) {
    const icon = getMediaTypeIcon(type);
    return `
        <div class="popover-model-section">
            <div class="popover-section-header">
                ${icon}
                ${title}
            </div>
            <div class="popover-model-grid">
                ${models.map(model => createClassicPopoverCard(model, type)).join('')}
            </div>
        </div>`;
}

function getMediaTypeIcon(type) {
    const icons = {
        image: '<svg viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>',
        video: '<svg viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect width="15" height="14" x="1" y="5" rx="2" ry="2"/></svg>',
        audio: '<svg viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>'
    };
    return (icons[type] || '').replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="2"');
}

function getModelLogoHtml(model) {
    let logoSvg = MODEL_LOGOS_SVG[model.model_name] || PROVIDER_LOGOS_SELECTOR[model.provider];
    if (logoSvg) {
        return logoSvg.includes('class="model-logo-main"') ? logoSvg : logoSvg.replace('class="model-logo"', 'class="model-logo-main"');
    }
    const fallbackText = model.displayNameMain ? model.displayNameMain.substring(0, 2).toUpperCase() : (model.provider ? model.provider.substring(0, 1).toUpperCase() : '?');
    return `<div class="model-logo-main model-logo-fallback" style="display: flex; align-items: center; justify-content: center; background: var(--bg-quaternary); border-radius: 6px; color: var(--text-secondary); font-weight: 600; font-size: 11px; border: 1px solid var(--border-color);">${fallbackText}</div>`;
}

function createClassicPopoverCard(model, type) {
    const isActive = model.model_name === document.querySelector('.model-selector').dataset.model;
    let classes = `model-card-popover ${isActive ? 'active' : ''} ${model.premium ? 'premium' : ''}`;

    const badgeHtml = model.premium && model.premium_icon && PREMIUM_ICONS_BADGES[model.premium_icon] 
        ? `<div class="premium-icon-badge badge-type-${model.premium_icon}">${PREMIUM_ICONS_BADGES[model.premium_icon]}</div>` 
        : '';
    
    const capabilities = model.capabilities ? Object.keys(model.capabilities).filter(key => model.capabilities[key]) : [];
    const capabilitiesHtml = capabilities.map(cap => {
        const capName = cap.charAt(0).toUpperCase() + cap.slice(1);
        const color = `var(--cap-${cap}-color)`;
        const bgOpacity = `var(--cap-${cap}-bg-opacity)`;
        return `<div class="capability-badge" style="--cap-main-color: ${color}; --cap-bg-opacity: ${bgOpacity};" title="${capName}">
                    ${CAPABILITY_ICONS[cap] || ''}
                </div>`;
    }).join('');

    return `
        <div class="${classes}" data-model="${model.model_name}" data-provider="${model.provider}" data-api-name="${model.api_name}" data-type="${type}">
            ${badgeHtml}
            ${getModelLogoHtml(model)}
            <div class="model-name-main">${model.displayNameMain || model.model_name}</div>
            ${model.displayNameSub ? `<div class="model-name-sub">${model.displayNameSub}</div>` : ''}
            <div class="model-capabilities-bottom">${capabilitiesHtml}</div>
        </div>`;
}

function selectModel(modelName, provider, apiName, type) {
    const modelSelector = document.querySelector('.model-selector');
    
    modelSelector.dataset.model = modelName;
    modelSelector.dataset.provider = provider;
    modelSelector.dataset.apiName = apiName;
    modelSelector.dataset.mediaType = type;

    document.getElementById('selectedModelName').textContent = modelName;
    
    const logoElement = document.querySelector('.model-selector .model-logo');
    let selectorLogoHtml = (MODEL_LOGOS_SVG[modelName] || PROVIDER_LOGOS_SELECTOR[provider] || '');
    logoElement.innerHTML = selectorLogoHtml.replace('class="model-logo-main"', 'class="model-logo"');

    document.querySelectorAll('.model-card-popover').forEach(card => card.classList.remove('active'));
    const activeCard = document.querySelector(`.model-card-popover[data-model="${modelName}"]`);
    if (activeCard) activeCard.classList.add('active');
    
    toggleModelPopover();
}

function addPopoverCardClickListeners() {
    document.querySelectorAll('.model-card-popover').forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault(); e.stopPropagation();
            const { model, provider, apiName, type } = card.dataset;
            selectModel(model, provider, apiName, type);
        });
    });
}

function addProviderToggleListeners() {
    document.querySelectorAll('.provider-section-header').forEach(header => {
        header.addEventListener('click', function() {
            const providerKey = this.dataset.provider;
            openProviderSections[providerKey] = !openProviderSections[providerKey];
            this.classList.toggle('open');
            this.nextElementSibling.classList.toggle('collapsed');
        });
    });
}

export function initializePopoverSearch() {
    const searchInput = document.getElementById('modelSearchInput');
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.model-card-popover').forEach(card => {
            const isMatch = card.dataset.model.toLowerCase().includes(searchTerm) || card.dataset.provider.toLowerCase().includes(searchTerm);
            card.style.display = isMatch ? 'flex' : 'none';
        });
        document.querySelectorAll('.provider-section-collapsible, .popover-model-section').forEach(section => {
            const visibleCards = section.querySelectorAll('.model-card-popover[style*="display: flex"], .model-card-popover:not([style*="display: none"])');
            section.style.display = visibleCards.length > 0 ? 'block' : 'none';
        });
    });
}

export function switchMediaType(type) {
    currentMediaType = type;
    document.querySelectorAll('.media-type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });

    renderModelPopoverContent();
    
    const firstModelCard = document.querySelector(`#${type}-section .model-card-popover`);
    if (firstModelCard) {
        const { model, provider, apiName } = firstModelCard.dataset;
        const modelSelector = document.querySelector('.model-selector');
        modelSelector.dataset.model = model;
        modelSelector.dataset.provider = provider;
        modelSelector.dataset.apiName = apiName;
        modelSelector.dataset.mediaType = type;
        document.getElementById('selectedModelName').textContent = model;
        // The API name element is gone, so no need to set it.
        const logoElement = document.querySelector('.model-selector .model-logo');
        logoElement.innerHTML = (MODEL_LOGOS_SVG[model] || PROVIDER_LOGOS_SELECTOR[provider] || '').replace('class="model-logo-main"', 'class="model-logo"');
    }
=======
// static/js/popover.js
import { MODEL_LOGOS_SVG, PROVIDER_LOGOS_SELECTOR, CAPABILITY_ICONS, PREMIUM_ICONS_BADGES } from './config.js';

let modelsData = null;
let isPopoverExpandedView = false;
let openProviderSections = {};
let currentMediaType = 'llm'; // Default media type

// --- Popover UI and State ---

export function toggleModelPopover() {
    const popover = document.getElementById('modelDropdown');
    const overlay = document.getElementById('modelDropdownOverlay');
    const selector = document.querySelector('.model-selector');
    const isOpen = popover.classList.toggle('active');
    overlay.classList.toggle('active', isOpen);
    selector.classList.toggle('active', isOpen);

    if (isOpen) {
        if (!modelsData) {
            initializeModels();
        }
        document.getElementById('modelSearchInput').focus();
    }
}

export function togglePopoverExpandedView(event) {
    if (event) event.stopPropagation();
    isPopoverExpandedView = !isPopoverExpandedView;
    renderModelPopoverContent();

    const btn = document.getElementById('popoverShowMoreBtn');
    const btnText = btn.querySelector('span');
    const btnIcon = btn.querySelector('svg.show-more-less-icon');

    if (isPopoverExpandedView) {
        btnText.textContent = 'Show less';
        btnIcon.innerHTML = `<path d="m18 15-6-6-6 6"></path>`;
    } else {
        btnText.textContent = 'Show all providers';
        btnIcon.innerHTML = `<path d="m6 9 6 6 6-6"></path>`;
    }
}

// --- Model Data and Rendering ---

async function initializeModels() {
    try {
        const response = await fetch('/models/categorized');
        if (!response.ok) throw new Error('Failed to fetch models');
        modelsData = await response.json();
        renderModelPopoverContent();
    } catch (error) {
        console.error(error);
        const popoverContent = document.getElementById('popoverScrollableContent');
        if (popoverContent) {
            popoverContent.innerHTML = '<p style="padding: 20px; text-align: center; color: var(--text-secondary);">Could not load models.</p>';
        }
    }
}

function renderModelPopoverContent() {
    if (!modelsData) return;

    const popoverContent = document.getElementById('popoverScrollableContent');
    popoverContent.innerHTML = '';

    const categories = {
        llm: { data: modelsData.llm_models || [] },
        image: { data: modelsData.image_models || [] },
        audio: { data: modelsData.audio_models || [] },
        video: { data: modelsData.video_models || [] }
    };

    for (const type in categories) {
        const category = categories[type];
        const section = document.createElement('div');
        section.className = `media-section ${type === currentMediaType ? 'active' : ''}`;
        section.id = `${type}-section`;
        
        if (category.data.length > 0) {
            section.innerHTML = (type === 'llm') 
                ? renderLlmsSection(category.data)
                : `<div class="popover-model-grid">${category.data.map(model => createPopoverModelCard(model, type)).join('')}</div>`;
        } else {
            section.innerHTML = `<p style="text-align:center; padding: 40px 20px; color: var(--text-secondary);">No models available for this type.</p>`;
        }
        popoverContent.appendChild(section);
    }

    addPopoverCardClickListeners();
    addProviderToggleListeners();
}

function renderLlmsSection(llmModels) {
    let html = '';
    const favorites = llmModels.slice(0, 6); // Show more favorites
    
    html += `
        <div class="popover-model-section">
            <div class="popover-section-header">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17v5"/><path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"/></svg>
                Favorites
            </div>
            <div class="popover-model-grid">
                ${favorites.map(m => createPopoverModelCard(m, 'llm')).join('')}
            </div>
        </div>`;

    if (isPopoverExpandedView) {
        const allOtherModels = llmModels.slice(6);
        const modelsByProvider = allOtherModels.reduce((acc, model) => {
            (acc[model.provider_name] = acc[model.provider_name] || []).push(model);
            return acc;
        }, {});

        for (const providerName in modelsByProvider) {
            const providerModels = modelsByProvider[providerName];
            const providerKey = providerModels[0].provider; // Get the lowercase key
            const isSectionOpen = openProviderSections[providerName] || false;
            let providerLogoHtml = (PROVIDER_LOGOS_SELECTOR[providerKey] || '').replace('class="model-logo"', 'class="model-logo-provider-header"');

            html += `
                <div class="provider-section-collapsible">
                    <div class="provider-section-header ${isSectionOpen ? 'open' : ''}" data-provider="${providerName}">
                        ${providerLogoHtml || `<span class="provider-logo-placeholder-header">${providerName.charAt(0).toUpperCase()}</span>`}
                        <span class="provider-name">${providerName}</span>
                        <span class="provider-model-count">(${providerModels.length})</span>
                        <svg class="provider-toggle-icon" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>
                    </div>
                    <div class="popover-model-grid provider-grid ${!isSectionOpen ? 'collapsed' : ''}">
                        ${providerModels.map(m => createPopoverModelCard(m, 'llm')).join('')}
                    </div>
                </div>`;
        }
    }
    return html;
}

// RESTORED HELPER FUNCTION
function getModelLogoHtml(model) {
    let logoSvg = MODEL_LOGOS_SVG[model.model_name] || PROVIDER_LOGOS_SELECTOR[model.provider];
    if (logoSvg) {
        return logoSvg.includes('class="model-logo-main"') ? logoSvg : logoSvg.replace('class="model-logo"', 'class="model-logo-main"');
    }
    return `<div class="model-logo-main" style="/* styles for placeholder */">${model.provider ? model.provider.substring(0,1).toUpperCase() : '?'}</div>`;
}

// RESTORED FULL-FEATURED CARD RENDERING
function createPopoverModelCard(model, type) {
    const modelSelector = document.querySelector('.model-selector');
    const selectedModelName = modelSelector.dataset.model;
    const isActive = model.model_name === selectedModelName;

    let classes = `model-card-popover`;
    if (isActive) classes += ' active';
    if (model.premium) classes += ' premium';

    const badgeHtml = model.premium && model.premium_icon && PREMIUM_ICONS_BADGES[model.premium_icon] 
        ? `<div class="premium-icon-badge badge-type-${model.premium_icon}">${PREMIUM_ICONS_BADGES[model.premium_icon]}</div>` : '';

    const capabilities = model.capabilities ? Object.keys(model.capabilities).filter(key => model.capabilities[key]) : [];
    const capabilityColors = {'vision': 'var(--cap-vision-color)', 'reasoning': 'var(--cap-reasoning-color)', 'coding': 'var(--cap-coding-color)', 'web': 'var(--cap-web-color)', 'docs': 'var(--cap-docs-color)'};
    const capabilityBgOpacities = {'vision': 'var(--cap-vision-bg-opacity)', 'reasoning': 'var(--cap-reasoning-bg-opacity)', 'coding': 'var(--cap-coding-bg-opacity)', 'web': 'var(--cap-web-bg-opacity)', 'docs': 'var(--cap-docs-bg-opacity)'};
    
    const capabilitiesHtml = capabilities.slice(0, 4).map(cap => 
        `<div class="capability-badge" style="--cap-main-color: ${capabilityColors[cap]}; --cap-bg-opacity: ${capabilityBgOpacities[cap]};" title="${cap.charAt(0).toUpperCase() + cap.slice(1)}">
            ${CAPABILITY_ICONS[cap] || ''}
        </div>`
    ).join('');

    return `
        <div class="${classes}" data-model="${model.model_name}" data-provider="${model.provider}" data-api-name="${model.api_name}" data-type="${type}">
            ${badgeHtml}
            ${getModelLogoHtml(model)}
            <div class="model-card-text-content">
                <div class="model-name-main">${model.displayNameMain}</div>
                ${model.displayNameSub ? `<div class="model-name-sub">${model.displayNameSub}</div>` : ''}
            </div>
            <div class="model-capabilities-bottom">${capabilitiesHtml}</div>
        </div>`;
}


async function selectModel(modelName, provider, apiName, type) {
    const modelSelector = document.querySelector('.model-selector');
    
    modelSelector.dataset.model = modelName;
    modelSelector.dataset.provider = provider;
    modelSelector.dataset.apiName = apiName;
    modelSelector.dataset.mediaType = type;

    document.getElementById('selectedModelName').textContent = modelName;
    document.getElementById('selectedModelApiName').textContent = apiName;

    const logoElement = document.querySelector('.model-selector .model-logo');
    logoElement.innerHTML = getModelLogoHtml({ model_name: modelName, provider: provider }).replace('class="model-logo-main"', 'class="model-logo"');

    document.querySelectorAll('.model-card-popover').forEach(card => card.classList.remove('active'));
    const activeCard = document.querySelector(`.model-card-popover[data-model="${modelName}"]`);
    if (activeCard) {
      activeCard.classList.add('active');
    }
    
    toggleModelPopover();
}

// --- Event Listener Setup ---

function addPopoverCardClickListeners() {
    document.querySelectorAll('.model-card-popover').forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const { model, provider, apiName, type } = card.dataset;
            selectModel(model, provider, apiName, type);
        });
    });
}

function addProviderToggleListeners() {
    document.querySelectorAll('.provider-section-header').forEach(header => {
        header.addEventListener('click', function() {
            const providerKey = this.dataset.provider;
            openProviderSections[providerKey] = !openProviderSections[providerKey];
            this.classList.toggle('open');
            this.nextElementSibling.classList.toggle('collapsed');
        });
    });
}

export function initializePopoverSearch() {
    const searchInput = document.getElementById('modelSearchInput');
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        
        document.querySelectorAll('.model-card-popover').forEach(card => {
            const modelName = card.dataset.model.toLowerCase();
            const providerName = card.dataset.provider.toLowerCase();
            const isMatch = modelName.includes(searchTerm) || providerName.includes(searchTerm);
            card.style.display = isMatch ? 'flex' : 'none';
        });

        document.querySelectorAll('.provider-section-collapsible, .popover-model-section').forEach(section => {
            const visibleCards = section.querySelectorAll('.model-card-popover[style*="display: flex"]');
            section.style.display = visibleCards.length > 0 ? 'block' : 'none';
        });
    });
}

export function switchMediaType(type) {
    currentMediaType = type;
    
    document.querySelectorAll('.media-type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });

    renderModelPopoverContent(); // Re-render the content for the new media type

    document.getElementById('modelSearchInput').value = '';
    initializePopoverSearch();
>>>>>>> 8d3172731d5e6e3861efbcbb51bc008a999da776
}