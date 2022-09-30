<template>
    <div class="text">
        <h3>Approach and Aim</h3>
        <p>
            The Museum für Naturkunde Berlin published annual reports since 1887. These appeared as
            part of the Chronik of the Friedrich-Wilhelms-Universität zu Berlin (today the
            Humboldt-Universität zu Berlin), as the museum was one of the institutes of the
            university in that time. The annual reports constitute a unique source that provides
            insight into the collection policies and the development of the museum in the periods
            between 1887-1915 and 1928-1938. Particularly, the various institutes and departments
            reported on the organisational structure of the museum, personnel changes, publications
            and lectures, use of space, development of the museum infrastructure, spatial
            arrangements, utilisation and growth of the individual museum collections as well as
            their scientific evaluation and curation.
            <br />
            Of critical importance for provenance research, the reports often include names of
            collectors and donors, as well as places of origin, and information on the inflow and
            outflow of objects. Since the reports mainly cover the decades of German colonial
            expansion, this source is a key resource to address the following research questions on
            the topics of, among others:
        </p>

        <ul>
            <li>
                institutional organisation in terms of budget, infrastructures, and scientific and
                non-scientific staff
            </li>
            <li>
                expansion of the collections from the beginning of the German colonial period to the
                era of National Socialism
            </li>
            <li>assessment of colonial objects in the collections</li>
            <li>identification of original regions and main collectors during this period</li>
            <li>reconstruction of the institutions' global and local networks</li>
            <li>history of the exhibition processes and taxidermy labour</li>
        </ul>

        <p>
            By opening this source for research this project will serve interdisciplinary interests
            of curators, collection and digitization managers, researchers, citizen scientists,
            educators, etc.
        </p>

        <p>The project aims to:</p>
        <ul>
            <li>
                produce semantic annotations of the text using the
                <a href="https://cidoc-crm.org" target="_blank">
                    CIDOC Conceptual Reference Model (CRM)
                </a>
                developed by the International Committee for Documentation (CIDOC) of the
                International Council of Museums (ICOM),
            </li>
            <li>
                model the annotations in a graph database in order to also integrate data from
                external sources as easily as possible as well as to offer other sources the
                possibility to embed the information of the annual reports into their own knowledge
                graphs,
            </li>
            <li>
                develop an online platform from which the information from the graph database can be
                easily accessed
            </li>
        </ul>
        <p>
            Our work builds upon the version of the Chronik
            <a
                href="http://www.digi-hub.de/viewer/resolver?urn=urn:nbn:de:kobv:11-d-6653534"
                target="_blank">
                digitized
            </a>
            by the Library of the Humboldt-University.
        </p>
        <h3>Status</h3>
        <p>
            All information found in the Chronik related to acquisitions of new objects by the
            Zoological Museum is annotated. In over 7500 annotated lines of over 32000 lines in
            total we processed nearly 39000 semantic entities. In this initial step, we tried to
            model the data as close to the source as possible – meaning that we neither validated
            the statements the authors made nor critically contextualised problematic terms related
            to racism and colonialism.
        </p>

        <p>
            12066 of the identified semantic entities portray individual acquisition of objects. The
            remaining entities are mostly connected to these acquisitions to describe each of the
            acquisitions in more detail and can be categorised this way:
        </p>
        <table class="table90">
            <tr>
                <th>Category</th>
                <th>No. of connected acquisitions</th>
                <th>Percentage of all acquisitions with this connection</th>
                <th>Examples</th>
            </tr>
            <tr>
                <td>Receiving collection</td>
                <td class="right">12058</td>
                <td class="right">99.9%</td>
                <td>
                    <span class="entityLink" @click="emitDisplayTextOf('4706')">Arachnoidea</span>
                    ,
                    <span class="entityLink" @click="emitDisplayTextOf('24160')">Würmer</span>
                </td>
            </tr>
            <tr>
                <td>Location</td>
                <td class="right">9510</td>
                <td class="right">78.8%</td>
                <td>
                    <span class="entityLink" @click="emitDisplayTextOf('44678')">
                        Deutsch-Neuguinea
                    </span>
                    ,
                    <span class="entityLink" @click="emitDisplayTextOf('10362')">
                        Tanganjika-See
                    </span>
                </td>
            </tr>
            <tr>
                <td>Supplier</td>
                <td class="right">9462</td>
                <td class="right">78.4%</td>
                <td>
                    <span class="entityLink" @click="emitDisplayTextOf('44753')">
                        Bezirksamtmann Dr. Reuß
                    </span>
                    ,
                    <span class="entityLink" @click="emitDisplayTextOf('44728')">
                        Fräulein Tomala
                    </span>
                </td>
            </tr>
            <tr>
                <td>Taxon</td>
                <td class="right">983</td>
                <td class="right">8.1%</td>
                <td>
                    <span class="entityLink" @click="emitDisplayTextOf('42815')">Aktinien</span>
                    ,
                    <span class="entityLink" @click="emitDisplayTextOf('47549')">
                        Ichneumoniden
                    </span>
                </td>
            </tr>
            <tr>
                <td>Dimension</td>
                <td class="right">844</td>
                <td class="right">7.0%</td>
                <td>
                    <span class="entityLink" @click="emitDisplayTextOf('17545')">zahlreiche</span>
                    ,
                    <span class="entityLink" @click="emitDisplayTextOf('45881')">vier</span>
                </td>
            </tr>
            <tr>
                <td>Condition State/ Condition Assessment</td>
                <td class="right">290</td>
                <td class="right">2.4%</td>
                <td>
                    <span class="entityLink" @click="emitDisplayTextOf('44695')">wertvoll</span>
                    ,
                    <span class="entityLink" @click="emitDisplayTextOf('38580')">
                        äußerst selten
                    </span>
                </td>
            </tr>
        </table>
        <p>
            We were generally able to identify the person or institution which transferred an object
            to a collection of the museum and the original location of this object. In total we
            found 2313 distinct giving persons/institutions and 1250 distinct locations.
        </p>
        <p>
            The acquisitions were categorised into three types, according to their descriptions in
            the text as “Gift”, “Purchase”, or “Trade”. A transaction is either classified as
            purchase if the supplier gets an amount of money in return for the objects or as trade
            if the supplier gets other objects or services from the museum in return for their
            objects or finally as gift if the supplier gets no apparent compensation in return for
            their objects. These three types are distributed like this:
        </p>
        <table class="table60">
            <tr>
                <th>Type</th>
                <th>No. of acquisitions</th>
                <th>Percentage of all acquisitions</th>
            </tr>
            <tr>
                <td>Gift</td>
                <td class="right">8869</td>
                <td class="right">73.5%</td>
            </tr>
            <tr>
                <td>Purchase</td>
                <td class="right">2587</td>
                <td class="right">21.4%</td>
            </tr>
            <tr>
                <td>Trade</td>
                <td class="right">608</td>
                <td class="right">5.0%</td>
            </tr>
        </table>

        <p>
            The number of our identified acquisitions tend to become more and more over the years
            until 1913, when the annual report was reduced to a minimum because they switched to
            another umbrella publication. The chronological distribution looks like this:
        </p>
        <AcquisitionsPerYear />

        <p>
            The annotated data is modelled in a
            <strong>knowledge graph</strong>
            . Every semantic entity is connected to at least another semantic entity via a labeled
            edge in order to preserve the context the entity is embedded in. The labels for
            classifying semantic entities and these so called properties are defined in the ontology
            of the
            <a href="https://cidoc-crm.org" target="_blank">
                CIDOC Conceptual Reference Model (CRM)
            </a>
            .
        </p>
        <p>
            The majority of the data is
            <strong>centered around an acquisition</strong>
            in order to maintain the textual context of it. The general data model looks like this:
        </p>

        <AcquisitionsModel :smaller="false" />

        <p>
            We decided to enrich the knowledge graph with
            <strong>artificial entities</strong>
            which have no explicit position in the source text because of:
        </p>
        <ol>
            <li>
                <strong>Ability to consolidate the entities over the years</strong>
                <br />
            </li>
            <li>
                <strong>Possibility to correctly reason with the CIDOC CRM ontology</strong>
                <br />
                In a lot of cases the acquisitions of a collection of the museums are described in a
                dense list-like fashion. The implicit context of such mentions makes us humans
                understand that it is an acquisition but in order to transfer this context into an
                abstract knowledge graph we needed to make this explicit. That is the reason that
                you can find many entities which have no content (that means textual fragment in the
                source). You can recognize these through the Keyword
                <strong>"(implicit)"</strong>
                instead of an textual phrase in the search results below.
            </li>
        </ol>
    </div>
</template>

<script setup>
    import { useRouter } from 'vue-router';
    import AcquisitionsPerYear from './SVG/AcquisitionsPerYear.vue';
    import AcquisitionsModel from './SVG/AcquisitionsModel.vue';

    const router = useRouter();

    function emitDisplayTextOf(entity_id) {
        router.push({ name: 'search', query: { id: entity_id } });
    }
</script>

<style scoped>
    .text {
        width: 60%;
        text-align: justify;
        margin-left: 20%;
        margin-right: 20%;
    }

    .table90 {
        width: 90%;
        margin-left: 5%;
    }

    .table60 {
        width: 60%;
        margin-left: 20%;
    }

    .right {
        text-align: right;
    }

    th,
    td {
        padding: 1ex;
        text-align: left;
    }

    th {
        border-bottom: 2px solid black;
    }

    table tr:nth-child(odd) {
        background-color: #fff;
    }

    .entityLink {
        display: inline-block;
        background: white;
        border: 2px solid white;
    }

    table tr:nth-child(odd) .entityLink {
        background-color: #f0f0f0;
        border: 2px solid #f0f0f0;
    }

    .entityLink:hover {
        cursor: pointer;
        border: 2px solid black;
    }

    @media screen and (max-width: 700px) {
        .text {
            width: 90%;
            margin-left: 5%;
            margin-right: 5%;
        }

        .table60,
        .table90 {
            width: 100%;
            margin-left: 0%;
        }
    }
</style>
