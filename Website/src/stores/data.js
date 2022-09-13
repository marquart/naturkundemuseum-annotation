import { defineStore } from "pinia";

export const useDataStore = defineStore("data", {
  state: () => ({
    loadError: false,
    errorMsg: "",
    entityClasses: [],

    entitiesMap: {}, //entity_id (as str): entity_obj
    properties: [],
    entities: [],
    texts: {}, //text_id: array of lines
    loading: true,
  }),

  actions: {
    async loadData() {
      const SemanticData = await fetch(import.meta.env.BASE_URL + "data/webdata.json").then(
        (res) => (res.ok && res.json()) || Promise.reject(res)
      );
      if (SemanticData == undefined) {
        this.errorMsg = "ERORR: unable to fetch 'webdata.json'";
        this.loadError = true;
        return false;
      }
      const SemanticClassStats = await fetch(import.meta.env.BASE_URL + "data/class_stats.json").then(
        (res) => (res.ok && res.json()) || Promise.reject(res)
      );
      if (SemanticClassStats == undefined) {
        this.errorMsg = "ERORR: unable to fetch 'class_stats.json'";
        this.loadError = true;
        return false;
      }

      this.entitiesMap = SemanticData.Entities;
      let properties = Object.values(SemanticData.Properties);
      properties.forEach(this.populateProperty);

      this.entities = Object.values(this.entitiesMap);
      this.texts = SemanticData.Texts;
      this.properties = properties;

      this.entityClasses = SemanticClassStats.Entities;
      console.log(this.entities.length);

      if (
        this.entities.length < 1 ||
        this.properties.length < 1 ||
        this.texts == undefined ||
        this.entitiesMap == undefined
      ) {
        this.errorMsg = "ERORR: unable to load data";
        this.loadError = true;
        return false;
      }
      this.loading = false;
      return true;
    },

    populateProperty(element) {
      element.source = this.entitiesMap[element.source];
      element.target = this.entitiesMap[element.target];

      if (
        Object.prototype.hasOwnProperty.call(element.source, "outgoingProps")
      ) {
        element.source.outgoingProps.push(element);
      } else {
        element.source.outgoingProps = [element];
      }

      if (
        Object.prototype.hasOwnProperty.call(element.target, "incomingProps")
      ) {
        element.target.incomingProps.push(element);
      } else {
        element.target.incomingProps = [element];
      }
    },
  },
});
