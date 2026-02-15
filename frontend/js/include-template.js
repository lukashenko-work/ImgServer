class HTMLTemplate extends HTMLElement {
    attributeChangedCallback(attribute, previous, next){
        fetch(next)
            .then(response => response.text())
            .then(html => this.innerHTML = html);
    }

    static get observedAttributes(){
        return [ "data-template" ];
    }
}

window.customElements.define("html-template", HTMLTemplate);