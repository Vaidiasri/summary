document.addEventListener('DOMContentLoaded', () => {
  const summarizeBtn = document.getElementById('summarize-btn');
  const btnText = summarizeBtn.querySelector('.btn-text');
  const loader = summarizeBtn.querySelector('.spinner');
  const errorContainer = document.getElementById('error-container');
  const summaryContainer = document.getElementById('summary-container');
  const summaryContent = document.getElementById('summary-content');

  // Backend API URL - matches the FastAPI default server
  const API_URL = 'http://127.0.0.1:8000/api/summarize';

  summarizeBtn.addEventListener('click', async () => {
    // 1. Get the current active tab
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const url = tab.url;

      // Ensure it's a YouTube URL
      if (!url.includes('youtube.com/watch') && !url.includes('youtu.be/')) {
        showError('Please open a YouTube video to summarize.');
        return;
      }

      // 2. Prepare UI for loading
      setLoadingState(true);
      hideError();
      hideSummary();

      // 3. Make request to the local backend
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch summary.');
      }

      // 4. Display result
      showSummary(data.summary);

    } catch (error) {
      console.error('Summarize Error:', error);
      showError(error.message || 'An error occurred while connecting to the backend. Ensure the backend is running.');
    } finally {
      setLoadingState(false);
    }
  });

  // UI Helpers
  function setLoadingState(isLoading) {
    if (isLoading) {
      summarizeBtn.disabled = true;
      btnText.style.display = 'none';
      loader.style.display = 'block';
    } else {
      summarizeBtn.disabled = false;
      btnText.style.display = 'block';
      loader.style.display = 'none';
      btnText.textContent = 'Summarize Again';
    }
  }

  function showError(msg) {
    errorContainer.textContent = msg;
    errorContainer.classList.remove('hidden');
  }

  function hideError() {
    errorContainer.classList.add('hidden');
    errorContainer.textContent = '';
  }

  function showSummary(text) {
    summaryContent.textContent = text;
    summaryContainer.classList.remove('hidden');
  }

  function hideSummary() {
    summaryContainer.classList.add('hidden');
    summaryContent.textContent = '';
  }
});
