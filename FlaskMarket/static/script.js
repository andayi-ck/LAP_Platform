


document.addEventListener("DOMContentLoaded", function () {
    // Set "Calculate age on" field to today's date by default
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("calc_date").value = today;

    // Prevent selecting future date for "Date of Birth"
    document.getElementById("dob").setAttribute("max", today);

    // Ensure "Calculate age on" cannot be set before the "Date of Birth"
    document.getElementById("dob").addEventListener("change", function () {
        let dobValue = this.value;
        document.getElementById("calc_date").setAttribute("min", dobValue);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    function openCalendar(inputId) {
        document.getElementById(inputId).showPicker();
    }

    // Attach click events to all calendar icons
    document.querySelectorAll(".calendar-icon").forEach(icon => {
        icon.addEventListener("click", function () {
            const inputId = this.previousElementSibling.id; // Get the corresponding input ID
            openCalendar(inputId);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".calendar-icon").forEach(icon => {
        icon.addEventListener("click", function () {
            let inputField = this.previousElementSibling;
            inputField.focus();  // Works in all browsers
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".calendar-icon").forEach(icon => {
        icon.addEventListener("click", function () {
            let inputField = this.previousElementSibling;
            inputField.showPicker();  // Opens date picker in supported browsers
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".calendar-icon").forEach(icon => {
        icon.addEventListener("click", function () {
            let inputField = this.previousElementSibling; // Get the input field
            if (inputField) {
                inputField.showPicker();  // Opens the date picker
            } else {
                console.error("Date input field not found!");
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".calendar-icon").forEach(icon => {
        icon.addEventListener("click", function () {
            let inputField = this.previousElementSibling;
            if (inputField) {
                inputField.focus();  // Works in all browsers
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("dob").value = ""; // Clears default placeholder
});



