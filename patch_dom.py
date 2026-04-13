import streamlit as st

def apply_dom_patch():
    """Aplica patch para evitar erros de DOM com extensões do Chrome"""
    st.markdown("""
        <script>
        if (typeof Node === "function" && Node.prototype) {
            const originalRemoveChild = Node.prototype.removeChild;
            Node.prototype.removeChild = function(child) {
                if (child.parentNode !== this) {
                    console.warn("DOM patch: Skipping removeChild from wrong parent");
                    return child;
                }
                return originalRemoveChild.call(this, child);
            };

            const originalInsertBefore = Node.prototype.insertBefore;
            Node.prototype.insertBefore = function(newNode, referenceNode) {
                if (referenceNode && referenceNode.parentNode !== this) {
                    console.warn("DOM patch: Skipping insertBefore with wrong reference");
                    return newNode;
                }
                return originalInsertBefore.call(this, newNode, referenceNode);
            };
        }
        </script>
    """, unsafe_allow_html=True)
