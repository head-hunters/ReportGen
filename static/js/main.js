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

            const module = existingModules[i - 1] || {}; //get existing module data if it is available

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


// Retrieve the contents of the previous modules
const existingModules = existingModulesElement
    ? JSON.parse(existingModulesElement.dataset.modules)
    : [];

if (moduleCount && moduleContainer) {

    // Restore saved modules when editing (Persistence)
    if (existingModules.length > 0) {
        createModules(existingModules.length, existingModules); // persistence
    }

    moduleCount.addEventListener("input", function () { // get module count input and create modules accordingly

        const count = parseInt(moduleCount.value);

        if (isNaN(count)) { // is number?
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

//Redirecting the user to the dashboard after 1 second

const confirm_form = document.getElementById("confirm_form");

if (confirm_form) {
    confirm_form.addEventListener("submit", function () {
        const button = this.querySelector("button[type='submit']");

        if (button) {
            button.disabled = true;
            button.textContent = "Generating...";
        }

        setTimeout(() => {
            window.location.href = "/dashboard.html";
        }, 1000);
    });
}