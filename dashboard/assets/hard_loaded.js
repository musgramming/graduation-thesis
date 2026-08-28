(function () {
    const HARD_RELOAD_FLAG = "__hard_reload__";

    document.addEventListener("keydown", function (event) {
        if (
            event.ctrlKey &&
            event.shiftKey &&
            event.key.toLowerCase() === "r"
        ) {
            sessionStorage.setItem(HARD_RELOAD_FLAG, "true");
        }
    });

    window.addEventListener("beforeunload", function () {
        if (sessionStorage.getItem(HARD_RELOAD_FLAG) !== "true") {
            return;
        }

        Object.keys(sessionStorage)
            .filter(key => key.startsWith("_dash_persistence."))
            .forEach(key => {
                sessionStorage.removeItem(key);
            });

        sessionStorage.removeItem(HARD_RELOAD_FLAG);
    });
})();