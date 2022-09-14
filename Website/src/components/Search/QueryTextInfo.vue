<template>
    <div>
        <p class="bttn" @click="isOpen = !isOpen">
            {{ isOpen ? '🡻' : '🡺' }} Info
        </p>
        <div v-show="isOpen" class="info">
            <p>
                The annotated data is modeled in a
                <strong>knowledge graph</strong>
                . Every semantic entity is connected to at least another
                semantic entity via a labeled edge in order to preserve the
                context the entity is embedded in. The labels for classifying
                semantic entities and these so called properties are defined in
                the ontology of the
                <a href="https://cidoc-crm.org" target="_blank">
                    CIDOC Conceptual Reference Model (CRM)
                </a>
                .
            </p>
            <p>
                The majority of the data is
                <strong>centered around an acquisition</strong>
                in order to maintain the textual context of it. The general data
                model looks like this:
            </p>

            <AcquisitionsModel :smaller="true" />

            <p>
                We decided to enrich the knowledge graph with
                <strong>artificial entities</strong>
                wich have no explicit position in the source text because of:
            </p>
            <ol>
                <li>
                    <strong>
                        Ability to consolidate the entities over the years
                    </strong>
                    <br />
                </li>
                <li>
                    <strong>
                        Possibility to correctly reason with the CIDOC CRM
                        ontology
                    </strong>
                    <br />
                    In a lot of cases the acquisitions of a collection of the
                    museums are described in a dense list-like fashion. The
                    implicit context of such mentions makes us humans understand
                    that it is an acquisition but in order to transfer this
                    context into an abstract knowledge graph we needed to make
                    this explicit. That is the reason that you can find many
                    entities which have no content (that means textual fragment
                    in the source). You can recognize these through the Keyword
                    <strong>"(implicit)"</strong>
                    instead of an textual phrase in the search results below.
                </li>
            </ol>
        </div>
    </div>
</template>

<script setup>
    import { ref } from 'vue';
    import AcquisitionsModel from '@/components/SVG/AcquisitionsModel.vue';

    const isOpen = ref(false);
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .bttn {
        text-align: left;
        color: #7da30b;
        border: 1px solid #fff0;
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
