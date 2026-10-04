document.addEventListener(
    "DOMContentLoaded",
    () => {

        const button =
            document.querySelector(
                ".generate-button"
            );


        if (button) {

            button
                .closest("form")
                .addEventListener(
                    "submit",
                    () => {

                        button.innerHTML =
                            "<span>AI is analyzing you...</span><strong>✦</strong>";

                        button.style.opacity =
                            "0.7";

                        button.style.pointerEvents =
                            "none";

                    }
                );

        }


        /* Mouse glow */

        const glow =
            document.querySelector(
                ".cursor-glow"
            );


        document.addEventListener(
            "mousemove",
            (event) => {

                if (glow) {

                    glow.style.left =
                        event.clientX + "px";

                    glow.style.top =
                        event.clientY + "px";

                }

            }
        );

    }
);