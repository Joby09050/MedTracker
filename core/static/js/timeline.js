document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('timeline-container');
    if (!container) return;

    const PAGE_SIZE = 5;
    const buttons = document.querySelectorAll('#filter-buttons .filter-pill');
    const items = container.querySelectorAll('.timeline-item');
    const loadMoreBtn = document.getElementById('timeline-load-more');
    const countEl = document.getElementById('timeline-count');
    const paginationEl = document.getElementById('timeline-pagination');

    let activeFilter = 'all';
    let currentPage = 1;

    function getFilteredItems() {
        return Array.from(items).filter(function (item) {
            const type = item.getAttribute('data-type');
            return activeFilter === 'all' || type === activeFilter;
        });
    }

    function updateTimelineConnectors(displayedItems) {
        items.forEach(function (item) {
            item.classList.remove('is-last-visible');
        });
        if (displayedItems.length) {
            displayedItems[displayedItems.length - 1].classList.add('is-last-visible');
        }
    }

    function updatePaginationUI(totalFiltered, displayedCount) {
        if (!paginationEl) return;

        if (totalFiltered === 0) {
            paginationEl.style.display = 'flex';
            paginationEl.classList.add('is-empty');
            if (countEl) countEl.textContent = 'No records match this filter.';
            if (loadMoreBtn) loadMoreBtn.style.display = 'none';
            return;
        }

        if (totalFiltered <= PAGE_SIZE) {
            paginationEl.style.display = 'none';
            return;
        }

        paginationEl.style.display = 'flex';
        paginationEl.classList.remove('is-empty');
        if (countEl) {
            countEl.textContent = 'Showing ' + displayedCount + ' of ' + totalFiltered + ' records';
        }
        if (loadMoreBtn) {
            loadMoreBtn.style.display = displayedCount < totalFiltered ? 'inline-flex' : 'none';
        }
    }

    function renderTimeline() {
        const filtered = getFilteredItems();
        const visibleLimit = currentPage * PAGE_SIZE;
        const displayed = filtered.slice(0, visibleLimit);

        items.forEach(function (item) {
            const type = item.getAttribute('data-type');
            const matchesFilter = activeFilter === 'all' || type === activeFilter;
            item.classList.toggle('is-filter-hidden', !matchesFilter);
            item.classList.toggle('is-page-hidden', true);
        });

        displayed.forEach(function (item) {
            item.classList.remove('is-page-hidden');
        });

        updateTimelineConnectors(displayed);
        updatePaginationUI(filtered.length, displayed.length);
    }

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            buttons.forEach(function (btn) {
                btn.classList.remove('active');
            });
            button.classList.add('active');
            activeFilter = button.getAttribute('data-filter');
            currentPage = 1;
            renderTimeline();
        });
    });

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function () {
            currentPage += 1;
            renderTimeline();
        });
    }

    renderTimeline();
});
