<template>
    <div class="text">
        <p>The Museum für Naturkunde Berlin published annual reports since 1887. These appeared as part of the Chronicle of the Friedrich-Wilhelms-University (today the  Humboldt-Universität zu Berlin), as the museum was one of the institutes of the university in that time. The annual reports constitute today a unique source that provides insight into the development of the museum and its collections in the periods between 1887-1915 and 1928-1938. Particularly, the various institutes and departments reported on the organisational structure of the museum, personnel changes, publications and lectures, use of space, development of the museum infrastructure, spatial arrangements, utilisation and growth of the individual museum collections as well as their scientific evaluation and curation. Of critical importance for provenance research, the reports often include names of collectors and donors, as well as places of origin, and information on the inflow and outflow of objects. Since the reports mainly cover the decades of German colonial expansion, this source is a key resource to address the following research questions on the topics of, among others:</p>

        <ul>
            <li>institutional organisation in terms of budget, infrastructures, and scientific and non-scientific staff</li>
            <li>expansion of the collections from the beginning of the German colonial period to the era of National Socialism</li>
            <li>assessment of colonial objects in the collections</li>
            <li>identification of original regions and main collectors during this period</li>
            <li>reconstruction of the institutions' global and local networks</li>
            <li>history of the exhibition processes and taxidermy labour</li>
        </ul>

        <p>By opening this source for research this project will serve interdisciplinary interests of curators, collection and digitization managers, researchers, citizen scientists, educators, etc.</p>

        <p>The project aims to:</p>
        <ul>
            <li>produce semantic annotations of the text using the <a href="https://cidoc-crm.org">CIDOC Conceptual Reference Model (CRM)</a> developed by the International Committee for Documentation (CIDOC) of the International Council of Museums (ICOM),</li>
            <li>model the annotations in a graph database in order to also integrate data from external sources as easily as possible as well as to offer other sources the possibility to embed the information of the annual reports into their own knowledge graphs,</li>
            <li>develop an online platform from which the information from the graph database can be easily accessed</li>
        </ul>
    </div>
</template>

<script>
export default {
    name: 'Info',
    props: {
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .text {
        width: 60%;
        text-align: justify;
        margin-left: 20%;
        margin-right: 20%;
    }

    @media screen and (max-width: 700px) {
        .text {
            width: 90%;
            margin-left: 5%;
            margin-right: 5%;
        }
    }
</style>
