function  createAnalytics() {
    let counter = 0;
    let is_destroyed = false;

    const listener = () => counter ++

    document.addEventListener('click', listener)

    return {
        destroy() {
            document.removeEventListener('click')
            is_destroyed = true
        },

        getClicks() {
            if (is_destroyed) {
                return 'destroyed'
            }
            return counter
        }
    }
}

window.analytics = createAnalytics()