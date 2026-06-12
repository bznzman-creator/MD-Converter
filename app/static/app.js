const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const convertBtn = document.getElementById('convertBtn');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const resultTitle = document.getElementById('resultTitle');
const preview = document.getElementById('markdownPreview');
const downloadLink = document.getElementById('downloadLink');

let selectedFile = null;

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle('error', isError);
}

function setFile(file) {
  selectedFile = file;
  convertBtn.disabled = !file;
  resultEl.classList.add('hidden');
  preview.value = '';
  setStatus(file ? `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)` : 'No file selected.');
}

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') fileInput.click();
});
fileInput.addEventListener('change', () => setFile(fileInput.files[0] || null));

['dragenter', 'dragover'].forEach(eventName => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(eventName => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove('dragover');
  });
});

dropzone.addEventListener('drop', (event) => {
  const file = event.dataTransfer.files[0];
  if (file) setFile(file);
});

convertBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append('file', selectedFile);

  convertBtn.disabled = true;
  setStatus('Converting file...');

  try {
    const response = await fetch('/api/convert', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Conversion failed.');

    preview.value = data.markdown || '';
    resultTitle.textContent = data.markdown_filename;
    downloadLink.href = data.download_url;
    downloadLink.setAttribute('download', data.markdown_filename);
    resultEl.classList.remove('hidden');
    setStatus(`Converted successfully: ${data.markdown_filename}`);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    convertBtn.disabled = false;
  }
});
