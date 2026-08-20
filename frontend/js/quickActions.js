// quickActions.js — Quick tab buttons send pre-defined text queries

const quickTabs = document.querySelectorAll('.quick-tab');

quickTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    // Set active tab
    quickTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    const query = tab.dataset.query;
    if (query) sendTextQuery(query);
  });
});
