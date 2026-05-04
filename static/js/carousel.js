(function () {
    const track = document.getElementById('carouselTrack');
    if (!track) return;

    const slides = track.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot');
    const progressBar = document.getElementById('carouselProgress');
    const total = slides.length;
    if (total === 0) return;

    let current = 0;
    let timer = null;
    let paused = false;
    const INTERVAL = 5000;

    function go(index) {
        current = (index + total) % total;
        slides.forEach((s, i) => s.classList.toggle('active', i === current));
        dots.forEach((d, i) => d.classList.toggle('active', i === current));
        resetProgress();
    }

    function next() { go(current + 1); }
    function prev() { go(current - 1); }

    function resetProgress() {
        if (!progressBar) return;
        progressBar.style.transition = 'none';
        progressBar.style.width = '0%';
        progressBar.offsetHeight; // force reflow
        progressBar.style.transition = 'width ' + INTERVAL + 'ms linear';
        progressBar.style.width = '100%';
    }

    function startAutoPlay() {
        stopAutoPlay();
        timer = setInterval(function () {
            if (!paused) next();
        }, INTERVAL);
        resetProgress();
    }

    function stopAutoPlay() {
        if (timer) clearInterval(timer);
    }

    var carousel = document.getElementById('carousel');
    if (carousel) {
        carousel.addEventListener('mouseenter', function () { paused = true; });
        carousel.addEventListener('mouseleave', function () { paused = false; resetProgress(); });
    }

    // touch support
    let touchStartX = 0;
    if (carousel) {
        carousel.addEventListener('touchstart', function (e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        carousel.addEventListener('touchend', function (e) {
            var diff = e.changedTouches[0].screenX - touchStartX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) prev(); else next();
                startAutoPlay();
            }
        }, { passive: true });
    }

    // expose to global for onclick handlers
    window.carouselNext = function () { next(); startAutoPlay(); };
    window.carouselPrev = function () { prev(); startAutoPlay(); };
    window.carouselGo = function (i) { go(i); startAutoPlay(); };

    // keyboard support
    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') { prev(); startAutoPlay(); }
        if (e.key === 'ArrowRight') { next(); startAutoPlay(); }
    });

    startAutoPlay();
})();
