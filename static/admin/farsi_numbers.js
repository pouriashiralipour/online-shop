function toFarsiNumber(n) {
    const farsiDigits = ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'];
    return n.replace(/\d/g, (x) => farsiDigits[parseInt(x)]);
}

function convertToFarsiNumbers() {
    const tags = ['span', 'td', 'th', 'a', 'label', 'div', 'input', 'strong'];

    tags.forEach(tag => {
        document.querySelectorAll(tag).forEach(el => {
            if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3) {
                el.textContent = toFarsiNumber(el.textContent);
            } else if (el.tagName === 'INPUT') {
                el.value = toFarsiNumber(el.value);
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", convertToFarsiNumbers);
