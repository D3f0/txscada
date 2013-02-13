
/*
 * GET home page.
 */

exports.index = function(req, res){
  
  res.render('index', {
    lista: [1, 2, 3, 4],
    title: "Listado de concentradores"
  });
};