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

const moduleCount = document.getElementById("modules");
const moduleContainer = document.getElementById("moduleContainer");
if (moduleCount && moduleContainer) {
    moduleCount.addEventListener("input", function () {
        const count = parseInt(moduleCount.value);
        if (isNaN(count)) {
            return
        }
        const currentCount = moduleContainer.children.length;


        if (count > currentCount) {


            for (let i = currentCount + 1; i <= count; i++) {
                moduleContainer.insertAdjacentHTML("beforeend", `
                    <div class="module mb-4">
                        <h5 class="mb-3">Module ${i}</h5>

                        <div class="mb-3">
            
                            <input type="text"
                            class="form-control"
                            name="module_name_${i}"
                            placeholder="Module Name">
                        </div>

                        <div class="mb-3">
            
                            <textarea class="form-control"
                            name="module_description_${i}"
                            rows="4"
                            placeholder="Module Description"></textarea>
                        </div>
                    </div>
                `);
            }

        }
        else if (count < currentCount) {
            while (moduleContainer.children.length > count) {
                moduleContainer.lastElementChild.remove();
            }
        }
    }
    )
};
