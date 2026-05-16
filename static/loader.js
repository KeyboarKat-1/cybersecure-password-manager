/* CyberSecure loader script
   Shows a premium full-screen loader and removes it when the page is ready.
   Uses timed terminal-style text updates and a fade-out transition. */
(function () {
    const loader = document.getElementById('cybersecure-loader');
    const subtitle = document.getElementById('loader-subtitle');
    const status = document.querySelector('.loader-status');
    const messages = [
        'Initializing Secure Vault...',
        'Establishing Secure Connection...',
        'Calibrating Encryption Matrix...',
        'Synchronizing Security Policies...',
        'Authenticating Enterprise Keys...'
    ];
    let currentMessage = 0;

    function updateStatusText() {
        if (!subtitle || !status) return;
        currentMessage = (currentMessage + 1) % messages.length;
        subtitle.textContent = messages[currentMessage];
        status.textContent = `Secure operation ${currentMessage + 1} / ${messages.length}`;
    }

    function finishLoader() {
        if (!loader) return;
        loader.classList.add('loader-hidden');
        document.documentElement.classList.remove('page-preloading');
        setTimeout(() => {
            if (loader.parentNode) {
                loader.parentNode.removeChild(loader);
            }
        }, 700);
    }

    if (!loader) return;
    document.documentElement.classList.add('page-preloading');

    const messageInterval = setInterval(updateStatusText, 3200);

    function onPageReady() {
        clearInterval(messageInterval);
        setTimeout(finishLoader, 420);
    }

    if (document.readyState === 'complete') {
        onPageReady();
    } else {
        window.addEventListener('load', onPageReady);
    }
})();
