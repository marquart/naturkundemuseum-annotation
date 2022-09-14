<template>
    <div id="heading">
        <img src="/icons/mfn-logo.png" alt="Naturkundemuseum Logo" />
        <div id="heading-text">
            <h1>Provenance research under the spotlight</h1>
            <h2>
                Digital Edition of the Annual Reports of the Museum 1887–1915
                and 1928–1938
            </h2>
        </div>
    </div>
    <div v-show="data.loadError || !loadError" class="content errormsg">
        <strong>ERROR: {{ data.errorMsg }}</strong>
    </div>

    <nav class="content" id="navigation">
        <RouterLink to="/">INFO</RouterLink>
        <RouterLink to="/search">SEARCH</RouterLink>
        <RouterLink :to="{ name: 'analysis', params: { mode: 'Suppliers' } }">
            ANALYZE
        </RouterLink>
        <RouterLink to="/explore">EXPLORE</RouterLink>
    </nav>
    <div class="content">
        <RouterView />

        <hr />
        <p>
            Our work builds upon the version of the Chronik
            <a
                href="http://www.digi-hub.de/viewer/resolver?urn=urn:nbn:de:kobv:11-d-6653534"
                target="_blank">
                digitized
            </a>
            by the Library of the Humboldt-University and is licensed under
            <a
                href="https://creativecommons.org/licenses/by-nc-sa/4.0/"
                target="_blank">
                CC-BY-NC-SA
            </a>
            .
        </p>
        <div id="impressumBox">
            <p id="impressumClick" @click="showImpressum = !showImpressum">
                Impressum
            </p>
            <p v-show="showImpressum">
                Museum für Naturkunde
                <br />
                Department 'Humanities of Nature'
                <br />
                Invalidenstraße 43
                <br />
                10115 Berlin, Germany
                <br />
                <br />
                Landesunmittelbare rechtsfähige Stiftung des öffentlichen Rechts
                <br />

                phone: +49 (0)30 889140-8591
                <br />
                fax: +49 (0)30 889140-8561
                <br />
                email: info(at)mfn.berlin
                <br />
                <br />

                Authorized representative person: Stephan Junker (Managing
                Director)
                <br />
                Editorial representative person:
                <a
                    href="https://www.museumfuernaturkunde.berlin/en/about/team/ina.heumann"
                    target="_blank">
                    Ina Heumann
                </a>
            </p>
        </div>
    </div>
</template>

<script setup>
    import { RouterLink, RouterView } from 'vue-router';
    import { useDataStore } from '@/stores/data';
    import { ref } from 'vue';

    const data = useDataStore();
    const loadError = data.loadData();

    const showImpressum = ref(false);
</script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    body {
        /*background: linear-gradient(to bottom, #ffffff,  #f0f0f0);*/
        background: #f0f0f0;
        background-attachment: fixed;
        background-size: cover;
        margin: 0;
        height: 100%;

        font-family: 'Roboto', 'Titillium Web', 'Open Sans',
            'Trade Gothic Next LT', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
        margin-top: 20px;
    }
    .content {
        margin-left: 5%;
        margin-right: 5%;
        margin-bottom: 5%;
        text-align: left;
        width: 90%;
        display: block;
        line-height: 1.5;
        font-size: 12pt;
    }

    #navigation {
        border-bottom: 3px solid #7da30b;
        height: auto;
        display: grid;
        grid-template-columns: auto auto auto auto;
        align-content: center;
        margin-bottom: 2em;
    }

    nav a {
        font-size: 1.2em;
        font-family: inherit;
        text-align: center;
        background: #ebebeb;
        color: black;
        font-weight: bold;
        padding-top: 0.5em;
        padding-bottom: 0.5em;
        border-bottom: 5px solid #00000000;
        text-decoration: none;
    }

    nav a:hover {
        cursor: pointer;
        border-bottom: 5px solid #7da30b;
        color: #7da30b;
    }

    nav a.router-link-active {
        background: #ffffff;
        color: #7da30b;
    }

    #heading {
        width: 90%;
        margin: 1%;
        display: grid;
        grid: 'logo headingText';
        align-items: center;
    }

    h1 {
        font-weight: bold;
        display: inherit;
    }

    h2 {
        font-weight: normal;
        display: inherit;
    }

    #heading-text {
        text-align: left;
        /*float: left;
        transform: translate(0, 100px);*/
        grid-area: 'headingText';
    }

    #heading img {
        height: 270px;
        grid-area: 'logo';
        /*position: relative;
        display: inline;
        float:left;
        margin-right: 10px;*/
    }

    .errormsg {
        font-size: 1.2em;
        font-family: inherit;
        text-align: center;
        background: red;
        color: white;
        border: 3px solid white;
        margin-bottom: 1ex;
    }

    #impressumBox {
        display: inline-block;
        border: 1px solid #7da30b;
        padding: 1ex;
    }

    #impressumClick {
        color: #7da30b;
        margin: 0px;
    }

    #impressumClick:hover {
        cursor: pointer;
        text-decoration: underline;
    }

    @media screen and (max-width: 700px) {
        #heading {
            grid:
                'logo'
                'headingText';
        }

        #navigation {
            grid-template-columns: auto;
        }
    }
</style>
