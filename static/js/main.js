/**
 * Smart File Toolkit — Main JavaScript
 * Handles: drag-and-drop, file upload, tool processing, toasts, animations
 */

/* ============================================================
   FEATHER ICONS INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.8 });
});

/* ============================================================
   NAVBAR SCROLL EFFECT
   ============================================================ */
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  });
}

/* ============================================================
   MOBILE MENU
   ============================================================ */
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');
if (navToggle && mobileMenu) {
  navToggle.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
    const spans = navToggle.querySelectorAll('span');
    if (mobileMenu.classList.contains('open')) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });
  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
      navToggle.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });
}

/* ============================================================
   TOAST NOTIFICATIONS
   ============================================================ */
function showToast(message, type = 'info', title = null, duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const icons = {
    success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  };
  const titles = { success: 'Success', error: 'Error', info: 'Info', warning: 'Warning' };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">${icons[type] || icons.info}</div>
    <div class="toast-body">
      <div class="toast-title">${title || titles[type]}</div>
      <div class="toast-msg">${message}</div>
    </div>
    <button class="toast-close" aria-label="Close">×</button>
  `;

  const dismiss = () => {
    toast.classList.add('removing');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  };
  toast.addEventListener('click', dismiss);
  toast.querySelector('.toast-close').addEventListener('click', (e) => { e.stopPropagation(); dismiss(); });

  container.appendChild(toast);
  if (duration > 0) setTimeout(dismiss, duration);
}

/* ============================================================
   FORMAT FILE SIZE
   ============================================================ */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

/* ============================================================
   TOOL PAGE LOGIC
   Handles all tool pages generically based on TOOL_TYPE constant
   ============================================================ */
(function () {
  // Only run on tool pages
  if (typeof TOOL_TYPE === 'undefined') return;

  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');
  const fileListWrapper = document.getElementById('fileListWrapper');
  const fileCountEl = document.getElementById('fileCount');
  const clearAllBtn = document.getElementById('clearAll');
  const actionBar = document.getElementById('actionBar');
  const convertBtn = document.getElementById('convertBtn');
  const uploadSection = document.getElementById('uploadSection');
  const processingSection = document.getElementById('processingSection');
  const resultSection = document.getElementById('resultSection');
  const downloadBtn = document.getElementById('downloadBtn');
  const convertAnotherBtn = document.getElementById('convertAnother');
  const qualitySlider = document.getElementById('qualitySlider');
  const qualityBadge = document.getElementById('qualityBadge');
  const qualityControl = document.getElementById('qualityControl');
  const imagePreviewWrapper = document.getElementById('imagePreviewWrapper');
  const imagePreview = document.getElementById('imagePreview');
  const fileInfoBar = document.getElementById('fileInfoBar');

  let selectedFiles = [];

  /* --- DRAG & DROP ---------------------------------------- */
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); });
    });
    ['dragleave', 'drop'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove('drag-over'); });
    });
    dropzone.addEventListener('drop', (e) => {
      const files = Array.from(e.dataTransfer.files);
      handleFiles(files);
    });
    dropzone.addEventListener('click', (e) => {
      if (!e.target.closest('label')) fileInput.click();
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', () => {
      handleFiles(Array.from(fileInput.files));
      fileInput.value = '';
    });
  }

  /* --- HANDLE FILES --------------------------------------- */
  function handleFiles(newFiles) {
    const isSingle = (TOOL_TYPE === 'pdf-compressor' || TOOL_TYPE === 'image-compressor');
    if (isSingle) {
      selectedFiles = [newFiles[0]].filter(Boolean);
    } else {
      selectedFiles = [...selectedFiles, ...newFiles].slice(0, 20);
    }
    renderFileList();
    updateUI();
  }

  /* --- RENDER FILE LIST ----------------------------------- */
  function renderFileList() {
    if (!fileList) return;
    fileList.innerHTML = '';

    selectedFiles.forEach((file, idx) => {
      const item = document.createElement('div');
      item.className = 'file-item';
      item.dataset.index = idx;

      const isImage = file.type.startsWith('image/');
      const isPDF = file.name.toLowerCase().endsWith('.pdf');

      let thumbHTML = '';
      if (isImage) {
        const url = URL.createObjectURL(file);
        thumbHTML = `<img src="${url}" class="file-thumb" alt="" />`;
      } else if (isPDF) {
        thumbHTML = `<div class="file-thumb pdf-thumb">PDF</div>`;
      }

      item.innerHTML = `
        ${TOOL_TYPE === 'pdf-merger' ? '<div class="drag-handle"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="9" y1="5" x2="9" y2="19"/><line x1="15" y1="5" x2="15" y2="19"/></svg></div>' : ''}
        ${thumbHTML}
        <div class="file-info-wrap">
          <div class="file-name" title="${file.name}">${file.name}</div>
          <div class="file-size-text">${formatFileSize(file.size)}</div>
        </div>
        <button class="file-remove" data-idx="${idx}" aria-label="Remove">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      `;
      fileList.appendChild(item);
    });

    // Image preview for image compressor
    if (TOOL_TYPE === 'image-compressor' && selectedFiles[0] && imagePreviewWrapper) {
      const file = selectedFiles[0];
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file);
        imagePreview.src = url;
        imagePreviewWrapper.style.display = 'block';
        if (fileInfoBar) fileInfoBar.textContent = `${file.name} · ${formatFileSize(file.size)}`;
      }
    }

    // Remove buttons
    fileList.querySelectorAll('.file-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const i = parseInt(btn.dataset.idx);
        selectedFiles.splice(i, 1);
        renderFileList();
        updateUI();
      });
    });

    // Drag to reorder (PDF merger)
    if (TOOL_TYPE === 'pdf-merger') initSortable();
  }

  /* --- SORTABLE (PDF Merger) ------------------------------ */
  function initSortable() {
    if (!fileList) return;
    let dragged = null;
    fileList.querySelectorAll('.file-item').forEach(item => {
      item.setAttribute('draggable', 'true');
      item.addEventListener('dragstart', () => { dragged = item; item.classList.add('dragging'); });
      item.addEventListener('dragend', () => { item.classList.remove('dragging'); dragged = null; });
      item.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (dragged && dragged !== item) {
          const bbox = item.getBoundingClientRect();
          const mid = bbox.top + bbox.height / 2;
          if (e.clientY < mid) fileList.insertBefore(dragged, item);
          else item.insertAdjacentElement('afterend', dragged);
          // Reorder selectedFiles array
          const items = [...fileList.querySelectorAll('.file-item')];
          selectedFiles = items.map(el => selectedFiles[parseInt(el.dataset.index)]).filter(Boolean);
          items.forEach((el, i) => el.dataset.index = i);
        }
      });
    });
  }

  /* --- UPDATE UI STATE ------------------------------------ */
  function updateUI() {
    const hasFiles = selectedFiles.length > 0;
    if (fileListWrapper) fileListWrapper.style.display = hasFiles ? 'block' : 'none';
    if (!hasFiles && imagePreviewWrapper) imagePreviewWrapper.style.display = 'none';
    if (fileCountEl) fileCountEl.textContent = selectedFiles.length;

    // Show quality control when file selected
    if (qualityControl) qualityControl.style.display = hasFiles ? 'block' : 'none';

    // Min 2 files for merger
    const isReady = TOOL_TYPE === 'pdf-merger' ? selectedFiles.length >= 2 : hasFiles;
    if (actionBar) actionBar.style.display = isReady ? 'block' : 'none';
  }

  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', () => {
      selectedFiles = [];
      renderFileList();
      updateUI();
    });
  }

  /* --- QUALITY SLIDER ------------------------------------- */
  if (qualitySlider && qualityBadge) {
    const updateSlider = () => {
      const val = qualitySlider.value;
      qualityBadge.textContent = val + '%';
      const pct = ((val - qualitySlider.min) / (qualitySlider.max - qualitySlider.min)) * 100;
      qualitySlider.style.setProperty('--val', pct + '%');
    };
    qualitySlider.addEventListener('input', updateSlider);
    updateSlider();
  }

  // Preset buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (qualitySlider) {
        qualitySlider.value = btn.dataset.value;
        qualitySlider.dispatchEvent(new Event('input'));
      }
    });
  });

  /* --- CONVERT / PROCESS ---------------------------------- */
  if (convertBtn) {
    convertBtn.addEventListener('click', processFiles);
  }

  async function processFiles() {
    if (selectedFiles.length === 0) return;

    // Validate for merger
    if (TOOL_TYPE === 'pdf-merger' && selectedFiles.length < 2) {
      showToast('Please add at least 2 PDF files to merge.', 'warning');
      return;
    }

    // Show processing section
    uploadSection.style.display = 'none';
    processingSection.style.display = 'block';
    resultSection.style.display = 'none';

    // Build FormData
    const formData = new FormData();
    const csrfToken = typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : '';
    formData.append('csrfmiddlewaretoken', csrfToken);

    if (TOOL_TYPE === 'photo-to-pdf') {
      selectedFiles.forEach(f => formData.append('images', f));
    } else if (TOOL_TYPE === 'pdf-merger') {
      selectedFiles.forEach(f => formData.append('pdfs', f));
    } else if (TOOL_TYPE === 'pdf-compressor') {
      formData.append('pdf', selectedFiles[0]);
      formData.append('quality', qualitySlider ? qualitySlider.value : 60);
    } else if (TOOL_TYPE === 'image-compressor') {
      formData.append('image', selectedFiles[0]);
      formData.append('quality', qualitySlider ? qualitySlider.value : 75);
    }

    const url = typeof CONVERT_URL !== 'undefined' ? CONVERT_URL : '';

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': csrfToken },
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || 'Processing failed. Please try again.');
      }

      showResult(data);

    } catch (err) {
      processingSection.style.display = 'none';
      uploadSection.style.display = 'block';
      showToast(err.message || 'An unexpected error occurred.', 'error');
    }
  }

  /* --- SHOW RESULT ---------------------------------------- */
  function showResult(data) {
    processingSection.style.display = 'none';
    resultSection.style.display = 'block';

    // Build download URL
    const baseUrl = typeof DOWNLOAD_BASE !== 'undefined' ? DOWNLOAD_BASE : '';
    const dlUrl = baseUrl.replace('__FILENAME__', data.filename);
    if (downloadBtn) downloadBtn.href = dlUrl;

    // Render stats
    const statsEl = document.getElementById('resultStats');
    if (statsEl) {
      let statsHtml = '';

      if (TOOL_TYPE === 'photo-to-pdf') {
        statsHtml = `
          <div class="result-stat"><span class="result-stat-value">${data.pages}</span><span class="result-stat-label">Pages</span></div>
          <div class="result-stat"><span class="result-stat-value">${data.file_size}</span><span class="result-stat-label">PDF Size</span></div>
        `;
      } else if (TOOL_TYPE === 'pdf-merger') {
        statsHtml = `
          <div class="result-stat"><span class="result-stat-value">${data.files_merged}</span><span class="result-stat-label">Files Merged</span></div>
          <div class="result-stat"><span class="result-stat-value">${data.total_pages}</span><span class="result-stat-label">Total Pages</span></div>
          <div class="result-stat"><span class="result-stat-value">${data.file_size}</span><span class="result-stat-label">File Size</span></div>
        `;
      } else if (TOOL_TYPE === 'pdf-compressor' || TOOL_TYPE === 'image-compressor') {
        statsHtml = `
          <div class="result-stat"><span class="result-stat-value">${data.original_size}</span><span class="result-stat-label">Original</span></div>
          <div class="result-stat"><span class="result-stat-value">${data.compressed_size}</span><span class="result-stat-label">Compressed</span></div>
          <div class="result-stat"><span class="result-stat-value">${data.savings_percent}%</span><span class="result-stat-label">Saved</span></div>
        `;
        if (TOOL_TYPE === 'image-compressor' && data.dimensions) {
          statsHtml += `<div class="result-stat"><span class="result-stat-value" style="font-size:0.9rem">${data.dimensions}</span><span class="result-stat-label">Dimensions</span></div>`;
        }
      }
      statsEl.innerHTML = statsHtml;
    }

    // Compression visual bar
    const vizEl = document.getElementById('compressionVisual');
    if (vizEl && (TOOL_TYPE === 'pdf-compressor' || TOOL_TYPE === 'image-compressor')) {
      const pct = Math.max(5, 100 - data.savings_percent);
      vizEl.innerHTML = `
        <div class="compression-bar-wrap">
          <span class="compression-bar-label">Original</span>
          <div class="compression-bar-outer">
            <div class="compression-bar-inner original" style="width:100%"></div>
          </div>
          <span class="compression-bar-size">${data.original_size}</span>
        </div>
        <div class="compression-bar-wrap">
          <span class="compression-bar-label">Compressed</span>
          <div class="compression-bar-outer">
            <div class="compression-bar-inner compressed" style="width:0%" data-target="${pct}%"></div>
          </div>
          <span class="compression-bar-size">${data.compressed_size}</span>
        </div>
        <div class="savings-badge">🎉 ${data.savings_percent}% size reduction</div>
      `;
      // Animate bar
      setTimeout(() => {
        const bar = vizEl.querySelector('.compression-bar-inner.compressed');
        if (bar) bar.style.width = bar.dataset.target;
      }, 100);
    }

    showToast('File processed successfully!', 'success');
    if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.8 });
  }

  /* --- CONVERT ANOTHER ------------------------------------ */
  if (convertAnotherBtn) {
    convertAnotherBtn.addEventListener('click', () => {
      selectedFiles = [];
      renderFileList();
      updateUI();
      resultSection.style.display = 'none';
      uploadSection.style.display = 'block';
      if (qualityControl) qualityControl.style.display = 'none';
      if (imagePreviewWrapper) imagePreviewWrapper.style.display = 'none';
    });
  }

})();

/* ============================================================
   ANIMATE ELEMENTS ON SCROLL
   ============================================================ */
(function () {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.tool-card, .feature-item, .about-card').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.08}s, transform 0.5s ease ${i * 0.08}s`;
    observer.observe(el);
  });
})();
