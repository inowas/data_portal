angular.module('dataportalApp', [
  'ui.router',
  'ngResource',
  'dataportalApp.services',
  'dataportalApp.controllers',
])
  .config(function ($interpolateProvider, $httpProvider, $resourceProvider, $stateProvider, $urlRouterProvider) {
    // Force angular to use square brackets for template tag
    // The alternative is using {% verbatim %}
    $interpolateProvider.startSymbol('[[').endSymbol(']]');

    // CSRF Support
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    // This only works in angular 3!
    // It makes dealing with Django slashes at the end of everything easier.
    $resourceProvider.defaults.stripTrailingSlashes = false;

    // Django expects jQuery like headers
    // $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';

    // Routing

    $urlRouterProvider.otherwise('/');
    $stateProvider
      .state('toolsList', {
        url: '/',
        views: {
            content: {
              controller: 'ToolsListController',
              templateUrl: '/static/tools-angular/partials/tools_info.html'
            },
            navbar:{
              controller: 'ToolsListController',
              templateUrl: '/static/tools-angular/partials/tools_side_bar.html'
            }
        }
      })
      .state('tool', {
        url: '/tool/{toolID}',
        views: {
            content: {
              controller: 'PropertyListController',
              templateUrl: '/static/tools-angular/partials/tool-descriptive.html'
            },
            navbar: {
              controller: 'ToolsListController',
              templateUrl: '/static/tools-angular/partials/tools_side_bar.html'
              }
          }
      });
  });