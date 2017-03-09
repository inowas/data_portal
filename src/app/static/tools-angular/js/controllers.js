angular.module('dataportalApp.controllers', [])
  .controller('ToolsListController', function ToolsListController($scope, ToolsService) {
  $scope.tools = ToolsService.getToolsList();

})
  .controller('PropertyListController', function PropertyListController($scope, PropertyListService, AuthUser) {
    var userID=AuthUser.id;
    var valueType = 4;
  
    $scope.propertyList = PropertyListService.query(
      {
        userID: userID,
        valueType: valueType
      }
    );


});



