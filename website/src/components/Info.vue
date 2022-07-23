<template>
    <div class="text">
        <h3>Approach and Aim</h3>
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
                <li>produce semantic annotations of the text using the <a href="https://cidoc-crm.org" target="_blank">CIDOC Conceptual Reference Model (CRM)</a> developed by the International Committee for Documentation (CIDOC) of the International Council of Museums (ICOM),</li>
                <li>model the annotations in a graph database in order to also integrate data from external sources as easily as possible as well as to offer other sources the possibility to embed the information of the annual reports into their own knowledge graphs,</li>
                <li>develop an online platform from which the information from the graph database can be easily accessed</li>
            </ul>
            <p>Our work builds upon the version of the chronicle <a href="http://www.digi-hub.de/viewer/resolver?urn=urn:nbn:de:kobv:11-d-6653534" target="_blank">digitized</a> by the Library of the Humboldt-University.</p>
        <h3>Status</h3>
            <p>All information found in the Chronik related to acquisitions of new objects is annotated. In over 7500 annotated lines of the over 32000 lines in total we processed nearly 39000 semantic entities.</p>

            <p>12066 of these portray individual acquisition of objects. The remaining entities describe each of the acquisitions in more detail and can be categorized this way:</p>
            <table class="connectedEntities">
                <tr><th>Category</th><th>No. of acquisitions</th><th>Percentage of all acquisitions</th></tr>
                <tr><td>Receiving collection</td><td class="right">12058</td><td class="right">99.9%</td></tr>
                <tr><td>Location</td><td class="right">9510</td><td class="right">78.8%</td></tr>
                <tr><td>Giver</td><td class="right">9462</td><td class="right">78.4%</td></tr>
                <tr><td>Taxon</td><td class="right">983</td><td class="right">8.1%</td></tr>
                <tr><td>Dimension</td><td class="right">844</td><td class="right">7.0%</td></tr>
                <tr><td>Condition State/ Condition Assessment</td><td class="right">290</td><td class="right">2.4%</td></tr>
            </table>
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

    .connectedEntities {
        width: 90%;
        margin-left: 5%;
    }

    .right {
        text-align: right;
    }

    th,td {
        padding: 1ex;
    }

    th {
        border-bottom: 2px solid black;
        text-align: left;
    }

    table tr:nth-child(odd) {
        background-color: #FFF;
    }

    @media screen and (max-width: 700px) {
        .text {
            width: 90%;
            margin-left: 5%;
            margin-right: 5%;
        }
    }
</style>
