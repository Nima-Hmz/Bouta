document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.querySelector(".dropdown");
    const button = document.querySelector(".dropdown-button");
    const dropdownList = document.querySelector(".dropdown-list");
    const searchBox = document.querySelector(".search-box");
    const form = document.querySelector("form"); // Assuming the dropdown is inside a form
    const hiddenInput = document.querySelector("#hidden-province"); // Hidden input to store selected value

    let selectedValue = ""; // Store selected value

    // Prevent the default form submission behavior when clicking the button
    button.addEventListener("click", function (event) {
        event.preventDefault(); // Prevent form submission
        dropdown.classList.toggle("active"); // Toggle the dropdown visibility
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!dropdown.contains(event.target)) {
            dropdown.classList.remove("active");
        }
    });

    // Handle item selection
    dropdownList.addEventListener("click", function (event) {
        if (event.target.tagName === "LI") {
            selectedValue = event.target.getAttribute("data-value"); // Store selected value
            button.textContent = event.target.textContent; // Update button text
            hiddenInput.value = selectedValue; // Update hidden input with the selected value
            button.classList.remove("error"); // Remove error style
            dropdown.classList.remove("active"); // Close dropdown
        }
    });

    // Filter options based on search input
    searchBox.addEventListener("input", function () {
        const searchValue = searchBox.value.toLowerCase();
        const items = dropdownList.querySelectorAll("li");

        items.forEach(function (item) {
            if (item.textContent.toLowerCase().includes(searchValue)) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    });

    // Form validation: Prevent form submission if no option is selected
    form.addEventListener("submit", function (event) {
        // Ensure the hidden input is populated before submitting
        if (!selectedValue) {
            event.preventDefault(); // Stop form submission
            button.classList.add("error"); // Add error style to button
            alert("لطفاً یک استان را انتخاب کنید."); // Show error message
        } else {
            hiddenInput.value = selectedValue; // Ensure hidden input has the selected value
        }
    });
});