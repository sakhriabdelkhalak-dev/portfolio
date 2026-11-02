(function(root){
  'use strict';
  const PRODUCTS = [
    {id:'pulse',name:'Casque sans fil Pulse',category:'audio',categoryLabel:'Audio',price:34900,stock:6,color:'Ivoire & sable',image:'images/headphones.jpg',tag:'Pour se plonger dans le son',description:'Un casque au format enveloppant et aux teintes douces, imaginé pour accompagner vos moments de musique.',features:['Arceau réglable','Coussinets souples','Format sans fil — concept de démonstration']},
    {id:'tempo',name:'Enceinte portable Tempo',category:'audio',categoryLabel:'Audio',price:22900,stock:8,color:'Orange terre cuite',image:'images/speaker.jpg',tag:'Le son vous accompagne',description:'Une petite enceinte textile et sa boucle de transport : un accessoire simple pour une ambiance musicale.',features:['Format compact','Revêtement textile','Boucle de transport']},
    {id:'studio',name:'Micro de bureau Studio',category:'studio',categoryLabel:'Studio',price:39900,stock:4,color:'Noir charbon',image:'images/microphone.jpg',tag:'Place à votre créativité',description:'Un micro sur pied de table pour illustrer un petit espace de création audio. Un concept de produit, sans promesse de performance technique.',features:['Pied de bureau inclus dans le visuel','Corps compact','Connectique USB — concept de démonstration']},
    {id:'keys',name:'Mini clavier MIDI Keys',category:'studio',categoryLabel:'Studio',price:64900,stock:3,color:'Blanc & noir',image:'images/keyboard.jpg',tag:'Vos idées prennent forme',description:'Un clavier musical compact avec touches et commandes, imaginé pour une sélection de matériel créatif accessible.',features:['Format de bureau','Touches et commandes intégrées','Produit fictif de démonstration']},
    {id:'solo',name:'Écouteurs filaires Solo',category:'audio',categoryLabel:'Audio',price:8900,stock:12,color:'Bleu nuit',image:'images/earphones.jpg',tag:'Les petits essentiels',description:'Des écouteurs filaires aux détails sobres, pour compléter cette collection audio de démonstration.',features:['Format intra-auriculaire','Câble souple','Finition bleu nuit']},
    {id:'arc',name:'Support de casque Arc',category:'accessories',categoryLabel:'Accessoires',price:12900,stock:9,color:'Bois clair & charbon',image:'images/stand.jpg',tag:'Chaque chose à sa place',description:'Un support aux lignes arrondies, mêlant une teinte bois claire et une base sombre pour organiser un coin musique.',features:['Support posé sur un bureau','Ligne courbe','Casque non inclus']},
  ].map(Object.freeze);
  Object.freeze(PRODUCTS);
  const find=id=>PRODUCTS.find(product=>product.id===id);
  const clean=text=>String(text||'').toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();
  const money=cents=>(cents/100).toLocaleString('fr-FR',{minimumFractionDigits:cents%100?2:0,maximumFractionDigits:2})+' DH';
  function normalizeCart(input){
    if(!Array.isArray(input))throw new Error('Panier illisible.');
    const quantities=new Map();
    for(const line of input){
      const product=find(line?.id);const quantity=line?.quantity;
      if(!product||!Number.isInteger(quantity)||quantity<1)continue;
      quantities.set(product.id,Math.min(product.stock,(quantities.get(product.id)||0)+quantity));
    }
    return [...quantities].map(([id,quantity])=>({id,quantity}));
  }
  function add(cart,id,quantity=1){
    const product=find(id);if(!product)throw new Error('Ce produit ne fait pas partie du catalogue.');
    const current=normalizeCart(cart);const existing=current.find(line=>line.id===id)?.quantity||0;
    if(!Number.isInteger(quantity)||quantity<1)throw new Error('Choisissez une quantité entière.');
    if(existing+quantity>product.stock)throw new Error(`La quantité démo est limitée à ${product.stock} exemplaires pour ce produit.`);
    return setQuantity(current,id,existing+quantity);
  }
  function setQuantity(cart,id,quantity){
    const product=find(id);if(!product)throw new Error('Produit inconnu.');
    if(!Number.isInteger(quantity)||quantity<0||quantity>product.stock)throw new Error(`La quantité doit être comprise entre 0 et ${product.stock}.`);
    const next=normalizeCart(cart).filter(line=>line.id!==id);if(quantity)next.push({id,quantity});return next;
  }
  function totals(cart){
    const items=normalizeCart(cart).map(line=>({...line,product:find(line.id),lineTotal:find(line.id).price*line.quantity}));
    const subtotal=items.reduce((sum,line)=>sum+line.lineTotal,0);
    const shipping=subtotal>0&&subtotal<50000?2500:0;
    return {items,count:items.reduce((sum,line)=>sum+line.quantity,0),subtotal,shipping,total:subtotal+shipping,remaining:Math.max(0,50000-subtotal)};
  }
  function favorites(input){return [...new Set(Array.isArray(input)?input.filter(id=>find(id)):[])];}
  function toggleFavorite(input,id){if(!find(id))throw new Error('Produit inconnu.');const ids=favorites(input);return ids.includes(id)?ids.filter(item=>item!==id):[...ids,id];}
  function filter(options={}){
    const query=clean(options.query);const max=Number.isFinite(options.maxPrice)?Math.max(0,options.maxPrice):70000;
    const ids=favorites(options.favorites);
    const list=PRODUCTS.filter(product=>(!options.category||options.category==='all'||product.category===options.category)&&product.price<=max&&(!options.favoritesOnly||ids.includes(product.id))&&(!query||clean(product.name+' '+product.description+' '+product.categoryLabel).includes(query)));
    if(options.sort==='price-asc')list.sort((a,b)=>a.price-b.price);if(options.sort==='price-desc')list.sort((a,b)=>b.price-a.price);return list;
  }
  const api={PRODUCTS,find,money,normalizeCart,add,setQuantity,totals,favorites,toggleFavorite,filter};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.LoopMarket=api;
})(typeof globalThis!=='undefined'?globalThis:window);
