// EDITE AQUI. dry_run=true: nada é enviado de verdade (status vira SIMULADA).
return [{ json: {
  sheet_id: 'COLE_AQUI_O_ID_DA_PLANILHA',
  dry_run: true,
  phone_number_id: 'COLE_AQUI_PHONE_NUMBER_ID_DA_META',
  graph_versao: 'v23.0', // confira a versão atual no painel da Meta
  janela_horas: 23,       // resposta grátis só dentro de 24h da última msg do cliente
} }];
