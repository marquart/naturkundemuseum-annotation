<template>
  <div id="app">
    <div id="heading">
      <img src="./assets/mfn-logo.png" alt="Naturkundemuseum Logo">
      <div id="heading-text">
        <h1>Provenance research under the spotlight</h1>
        <h2>Digital Edition of the Annual Reports of the Museum 1887–1915 and 1928–1938</h2>
      </div>
    </div>

    <div class="content" id="navigation">

      <div class="selectmode" :style="infoNavStyle" @click="navigate(0)">Info</div>
      <div class="selectmode" :style="searchNavStyle" @click="navigate(1)">Construct Query</div>
      <div class="selectmode" :style="vizNavStyle" @click="navigate(2)">Visualizations</div>

    </div>
    <div class="content">
      <Info  v-show="mode === 0" />
      <Query v-show="mode === 1" @displayGraphOf="setDisplayGraphOf"/>
      <Visualizations v-show="mode === 2" :entityId="displayGraphOfEntitity"/>
    </div>
  </div>
</template>

<script>
//import HelloWorld from './components/Column.vue'
import Info from './components/Info.vue'
import Query from './components/Query.vue'
import Visualizations from './components/Visualizations.vue'


export default {
  name: 'App',
  components: {
    Info,
    Query,
    Visualizations
  },
  data() {
    return {
      infoNavStyle: {background: '#ffffff'},
      searchNavStyle: {background: '#EBEBEB'},
      vizNavStyle: {background: '#EBEBEB'},
      mode: 0,
      displayGraphOfEntitity: "-1"
    }
  },

  methods: {
    navigate(mode) {
      this.mode = mode;
      if (this.mode === 0) {
        this.infoNavStyle.background = '#ffffff';
        this.searchNavStyle.background = '#EBEBEB';
        this.vizNavStyle.background = '#EBEBEB';
      } else if (this.mode === 1) {
        this.infoNavStyle.background = '#EBEBEB';
        this.searchNavStyle.background = '#ffffff';
        this.vizNavStyle.background = '#EBEBEB';
      } else if (this.mode === 2) {
        this.infoNavStyle.background = '#EBEBEB';
        this.searchNavStyle.background = '#EBEBEB';
        this.vizNavStyle.background = '#ffffff';
      }

    },
    setDisplayGraphOf(item_id) {
      this.displayGraphOfEntitity = item_id;
      this.navigate(2);
    },

  },
}
</script>

<style>
  /*@import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');*/
  @import url('https://fonts.googleapis.com/css2?family=Titillium+Web&display=swap');

  body {
    /*background: linear-gradient(to bottom, #ffffff,  #f0f0f0);*/
    background: #f0f0f0;
    background-attachment: fixed;
    background-size: cover;
    margin: 0;
    height: 100%;
  }

  #app {
    font-family: "Titillium Web", "Open Sans", "Trade Gothic Next LT", Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    margin-top: 20px;
  }

  .content {
    margin-left: 5%;
    margin-right: 5%;
    text-align: left;
    width: 90%;
    display: block;
    line-height: 1.5;
  }

  #navigation {
    border-bottom: 3px solid #7da30b;
    height: auto;
    display: grid;
    grid-template-columns: auto auto auto;
    align-content: center;

  }

  .selectmode {
    font-size: 1.2em;
    font-family: inherit;
    text-align: center;
    background: #ffffff;
    color: black;
    padding-top: 0.5em;
    padding-bottom: 0.5em;

  }

  .selectmode:hover {
      cursor: pointer;
    }

  img {

  }

  #heading {
    width: 90%;
    margin: 1%;
    display: grid;
    grid: 
      'logo headingText';
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
</style>
