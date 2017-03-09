// Resources have the following methods by default:
// get(), query(), save(), remove(), delete()

// angular.module('dataportalApp.services', ['ngResource'])
//   .factory('Dataset', function($resource) {
//     return $resource('/api/modelobjects/{id}/'); 
//     // return $resource(
//     //   '/api/datasets/:id/'
//       // {},
//       // {query: {method:'GET', params:{}, isArray: true}
//     }); 


angular.module('dataportalApp.services', [])
  .service('ToolsService', function() {
      this.getToolsList = function(){
          var tools = [
              {
                id:0,
                descr: "Calculates descriptive statistical parameters of a single series.",
                name: "Descriptive analysis"
              },
              {
                id:1,
                descr: "Does something.",
                name: "Tool2"
              },
              {
                id:2,
                descr: "Does something.",
                name: "Tool3"
              }
            ];
          return tools;
      };
  })
  .service('PropertyListService', function($resource) {
    return $resource('/api/properties/');
  });
