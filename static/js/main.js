//Applying form-control to each input tag
const inputs = document.querySelectorAll("input")

inputs.forEach(input => {
    input.classList.add("form-control")

})

// Displaying error messages
const flashModal = document.getElementById("flashModal");
if (flashModal) {
    const modal = new bootstrap.Modal(flashModal);
    modal.show();
}



// Dynamic Module Generation

// Persistence Implementation
function createModules(count, existingModules = []) {

    const currentCount = moduleContainer.children.length;

    // Add modules (User increases Module Count)
    if (count > currentCount) {

        for (let i = currentCount + 1; i <= count; i++) {

            const module = existingModules[i - 1] || {};

            moduleContainer.insertAdjacentHTML("beforeend", `
                <div class="module mb-4">

                    <h5 class="mb-3">Module ${i}</h5>

                    <div class="mb-3">
                        <input
                            type="text"
                            class="form-control"
                            name="module_name_${i}"
                            placeholder="Module Name"
                            value="${module.name || ""}">
                    </div>

                    <div class="mb-3">
                        <textarea
                            class="form-control"
                            name="module_description_${i}"
                            rows="4"
                            placeholder="Module Description">${module.description || ""}</textarea>
                    </div>

                </div>
            `);
        }
    }

    // Remove modules (When the user decreases Module Count)
    else if (count < currentCount) {

        while (moduleContainer.children.length > count) {
            moduleContainer.lastElementChild.remove();
        }
    }
}


const moduleCount = document.getElementById("modules");
const moduleContainer = document.getElementById("moduleContainer");

const existingModulesElement = document.getElementById("existingModules");

const existingModules = existingModulesElement
    ? JSON.parse(existingModulesElement.dataset.modules)
    : [];

if (moduleCount && moduleContainer) {

    // Restore saved modules when editing (Persistence)
    if (existingModules.length > 0) {
        createModules(existingModules.length, existingModules);
    }

    moduleCount.addEventListener("input", function () {

        const count = parseInt(moduleCount.value);

        if (isNaN(count)) {
            return;
        }

        createModules(count);
    });
}



// Clearing Forms

const projectForm = document.getElementById("projectForm");

if (projectForm) {
    projectForm.addEventListener("reset", function () {
        moduleContainer.innerHTML = "";

    });
}

//Redirecting the user to the dashboard after pdf generation (Let js handle pdf downloading)

const confirm_form = document.getElementById("confirm_form")

if (confirm_form) {
    confirm_form.addEventListener("submit", async function (event) {
        event.preventDefault(); //prevents the form from sending a POST request

        const button = this.querySelector("button[type='submit']");
        const original_text = button.textContent.trim();
        button.disabled = true;
        button.textContent = "Generating...";




        try {
            const response = await fetch(this.action, { //sends a post request to the /confirm path
                method: "POST"
            });

            if (!response.ok) {
                throw new Error("Failed to generate PDF");
            }

            const filename = response.headers.get("Filename");
            const blob = await response.blob(); //convert response into blob since a pdf is binary data

            // create temp url and click it to trigger the download
            const url = window.URL.createObjectURL(blob);

            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
            link.click();

            window.URL.revokeObjectURL(url);

            // redirects the user to the dashboard
            window.location.href = "/dashboard.html";

        } catch (error) {
            console.error(error);
            alert("Something went wrong while generating the PDF");

            //Make the generate button accessible again
            button.disabled = false;
            button.textContent = original_text;
        }
    })
};