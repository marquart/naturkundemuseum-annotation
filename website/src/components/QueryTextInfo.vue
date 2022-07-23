<template>
    <div>
        <p class="bttn" @click="toggleIsOpen">{{isOpen ? '🡻': '🡺'}} Info</p>
        <div v-show="isOpen" class="info">
            The annotated data is modeled in a knowledge graph. Every semantic entity is connected to at least another semantic entity via a labeled edge in order to preserve the context the entity is embedded in. The labels for clasifying semantic entities and these so called properties are defined in the Ontology of the <a href="https://cidoc-crm.org" target="_blank">CIDOC Conceptual Reference Model (CRM)</a>.
        </div>
    </div>
</template>

<script>

export default {
    name: 'QueryTextInfo',
    components: {
    },

    props: {
    },

    data() {
        return {
            isOpen: false
        }
    },

    methods: {
        toggleIsOpen() {
            this.isOpen = !this.isOpen;
        },

    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .bttn {
        text-align: left;
        color: #7da30b;
        border: 1px solid #FFF0;
        padding: 1ex;
    }

    .bttn:hover {
        cursor: pointer;
        border: 1px solid #7da30b;
    }

    .info {
        width: 94%;
        margin-left: 3%;
        margin-right: 3%;
    }

    @media screen and (max-width: 1000px) {

    }
</style>
