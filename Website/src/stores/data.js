import { defineStore } from 'pinia';

export const useDataStore = defineStore('data', {
    state: () => ({
        loadError: false,
        errorMsg: '',
        entityClasses: [],

        entitiesMap: {}, //entity_id (as str): entity_obj
        properties: [],
        entities: [],
        texts: {}, //text_id: array of lines
        loading: true,

        // Analysis Data
        anaLoadError: false,
        anaErrorMsg: '',
        anaLoading: true,

        personsLookup: {},
        locationsLookup: {},
        collectionsLookup: {},
        personTable: {},
        locationsTable: {},
        collectionsTable: {},
    }),

    actions: {
        async loadBaseData() {
            const httpHeader = new Headers({
                'Accept-Encoding': 'gzip',
                'Content-type': 'application/json',
            });

            const SemanticData = await fetch(import.meta.env.BASE_URL + 'data/webdata.json.gz', {
                headers: httpHeader,
            }).then((res) => (res.ok && res.json()) || Promise.reject(res));
            if (SemanticData == undefined) {
                this.errorMsg = "ERORR: unable to fetch 'webdata.json.gz'";
                this.loadError = true;
                return false;
            }
            const SemanticClassStats = await fetch(
                import.meta.env.BASE_URL + 'data/class_stats.json.gz',
                { headers: httpHeader }
            ).then((res) => (res.ok && res.json()) || Promise.reject(res));
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
                this.errorMsg = 'ERORR: unable to load data';
                this.loadError = true;
                return false;
            }
            this.loading = false;
            return true;
        },

        async loadAnalysisData() {
            const httpHeader = new Headers({
                'Accept-Encoding': 'gzip',
                'Content-type': 'application/json',
            });
            const rslt = await Promise.all([
                fetch(import.meta.env.BASE_URL + 'data/Persons.json.gz', {
                    headers: httpHeader,
                }).then((res) => (res.ok && res.json()) || Promise.reject(res)),
                fetch(import.meta.env.BASE_URL + 'data/Locations.json.gz', {
                    headers: httpHeader,
                }).then((res) => (res.ok && res.json()) || Promise.reject(res)),
                fetch(import.meta.env.BASE_URL + 'data/Collections.json.gz', {
                    headers: httpHeader,
                }).then((res) => (res.ok && res.json()) || Promise.reject(res)),
            ]).then((data) => {
                // handle data array here
                if (
                    data == undefined ||
                    data.length != 3 ||
                    data[0] == undefined ||
                    data[1] == undefined ||
                    data[2] == undefined
                ) {
                    this.anaErrorMsg = "Couldn't fetch data from backend!";
                    this.anaLoadError = true;
                    return false;
                } else {
                    this.anaErrorMsg = false;
                    //Persons
                    this.personsLookup = data[0][0];
                    this.personTable = data[0][1];
                    //Locations
                    this.locationsLookup = data[1][0];
                    this.locationsTable = data[1][1];
                    //Collections
                    this.collectionsLookup = data[2][0];
                    this.collectionsTable = data[2][1];
                }
            });
            this.anaLoading = false;
            return true;
        },

        populateProperty(element) {
            element.source = this.entitiesMap[element.source];
            element.target = this.entitiesMap[element.target];

            if (Object.prototype.hasOwnProperty.call(element.source, 'outgoingProps')) {
                element.source.outgoingProps.push(element);
            } else {
                element.source.outgoingProps = [element];
            }

            if (Object.prototype.hasOwnProperty.call(element.target, 'incomingProps')) {
                element.target.incomingProps.push(element);
            } else {
                element.target.incomingProps = [element];
            }
        },
    },
});
