$(document).ready(function () {
    const $form = $('#contact-form');
    if (!$form.length) return;

    const $fields = $form.find('input[required], textarea[required], input[type=email]');

    $fields.on('blur', function () {
        validateField(this);
    });

    $form.on('submit', function (e) {
        let allValid = true;
        $fields.each(function () {
            if (!validateField(this)) allValid = false;
        });
        if (!allValid) e.preventDefault();
    });

    function validateField(field) {
        const valid = field.checkValidity();
        $(field).removeClass('is-valid is-invalid').addClass(valid ? 'is-valid' : 'is-invalid');
        return valid;
    }
});
