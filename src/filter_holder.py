use  <oscad_utils/chamfer.scad>

// La base donde va el filtro.
// Dimensiones exteriores
base_filtro_x = 39.5;
base_filtro_y = 80;
base_filtro_z = 8;

// Tamano del filtro lf102249
// http://www.deltaopticalthinfilm.com/product/lv-vis-bandpass-filter-b/

filtro_x = 25;
filtro_y = 60;
filtro_z = 2.5;
tol_filtro = 0.4;

// incluyendo tolerancias, para que el filtro quepa bien
filtrotol_x = 25 + tol_filtro;
filtrotol_y = 60 + tol_filtro;
filtrotol_z = 2.5 + tol_filtro/2; //mitad de tolerancia eje Z

// el hueco debajo del filtro (para que pase la luz)
// y que sea suficiente para sostener el filtro
dismin_soporte_filtro = 4; 
soporte_filtro_x = filtro_x - dismin_soporte_filtro;
soporte_filtro_y = filtro_y - dismin_soporte_filtro;
bisel = 1;  //radio del bisel

// -------------------------- BASE DEL FILTRO ---------------------------------------
// Esta diferencia es la base del filtro

difference () {

// La base del filtro, centrada en el eje X
translate([0,-base_filtro_y/2,0]) cube([base_filtro_x, base_filtro_y, base_filtro_z]);

// El hueco del filtro
translate ([(base_filtro_x-filtrotol_x)/2,
            -filtrotol_y/2,
            base_filtro_z - filtrotol_z/2])
   cube([filtrotol_x, filtrotol_y, filtrotol_z+1]);
   //el +1 del eje Z es para evitar non-manifold

// El hueco del filtro, que sujeta al filtro y que deja pasar la luz
union () {
for (x=[-1,1])
    for (y=[-1,1])
        translate([
          base_filtro_x/2 + x * (soporte_filtro_x/2-bisel),
          y * (soporte_filtro_y/2 - bisel),
          -1])
         cylinder (r=bisel, h=base_filtro_z+2,$fa=1, $fs=0.5);
    
  //Largo en X, y corto en Y
  translate([(base_filtro_x-soporte_filtro_x)/2,
            -(soporte_filtro_y/2-bisel),
            -1]) 
    cube ([soporte_filtro_x,soporte_filtro_y-2*bisel, base_filtro_z +2]);
    
 translate([(base_filtro_x-soporte_filtro_x)/2+bisel,
            -(soporte_filtro_y/2),
            -1]) 
    cube ([soporte_filtro_x-2*bisel,soporte_filtro_y, base_filtro_z +2]);
    
 
}
 
// chaflanes 

r_fillet = 5;
translate ([base_filtro_x,  base_filtro_y/2, 0]) 
  redondeo_xy (r_fillet=r_fillet, h_fillet=base_filtro_z);

translate ([base_filtro_x,  -base_filtro_y/2, 0]) 
  redondeo_xmy (r_fillet=r_fillet, h_fillet=base_filtro_z);

}

  
// ------------------------------ SOPORTE VERTICAL QUE UNE CON LA GUIA ----------------
// soporte que va a la guia

sop_guia_x = 12;
sop_guia_y = base_filtro_y;
sop_guia_z = 45;

despl_sop_guia_x = 8; // que se desplaza hacia atras, el resto se solapa con la base_filtro


top_hole_mgn12h = 20; // Distancia vertical de la guia MGN12H
top_hole_seb = 25; // Distancia vertical de las guias SEBLV16 y SEBS15
y_dist_seb = 20; // Distancia y (a lo largo del carril) de las guias SEBLV16 y SEBS15, y MGN12H


// medidas taladros
low_hole_z = 14;
// donde en la X empieza el taladro, lo que se va para atras, + el milimetro para evitar non-manifold
hole_x = despl_sop_guia_x+1; 

// Radio de los taladros M4
m4_r = 2.15; // diametro 4.3, 0.3 de tolerancia


//cabeza_m4_r = 3.65; // diametro 7.3mm. La cabeza es de 7
cabeza_m4_r = 3.7; // v05: diametro 7.4mm. La cabeza es de 7

// Radio de los taladros M3
m3_r = 1.6; // diametro 3.2, 0.2 de tolerancia
//cabeza_m3_r = 2.85; // diametro 5.7mm. La cabeza es de 5.5
cabeza_m3_r = 2.9; // v05: diametro 5.8mm. La cabeza es de 5.5

module tornillo (radio, radio_cabeza)
{
  union () {
    translate([-hole_x,0,low_hole_z])rotate([0,90,0])
      cylinder(r=radio, h=sop_guia_x, $fa=1, $fs=0.5);

    translate([0,0,low_hole_z])rotate([0,90,0])
      cylinder(r=radio_cabeza,h= sop_guia_x-despl_sop_guia_x+1,$fa=1, $fs=0.5);
}
}


// Necesito hacer la cabeza de dos y unirlas
module cabeza_tornillo (radio_cabeza)
{
    translate([0,0,low_hole_z])rotate([0,90,0])
      cylinder(r=radio_cabeza,h= sop_guia_x-despl_sop_guia_x+1,$fa=1, $fs=0.5);
}

module vastago_tornillo (radio)
{
    translate([-hole_x,0,low_hole_z])rotate([0,90,0])
      cylinder(r=radio, h=sop_guia_x, $fa=1, $fs=0.5);    
}


// Dimension del hueco
//grosor_atrapa_gt2 = 2.8; //el grosor del gt2 es 1.38mm, como van dos pegadas, seria como 2mm, le pongo 2.8
grosor_atrapa_gt2 = 3;

// Dimensiones del bloque que atrapa la correa: bl
largo_bl_atrapa_gt2 = 14;
alto_bl_atrapa_gt2 = 8; // el ancho (que es alto) de la correa es 6mm
x_bl_atrapa_gt2 = (sop_guia_x-grosor_atrapa_gt2)/2;

//pos_z_atrapa_gt2 = low_hole_z + top_hole_thorlabs_z;
//pos_z_atrapa_gt2 = sop_guia_z - alto_bl_atrapa_gt2;
pos_z_atrapa_gt2 = sop_guia_z;

// referenciado a la esquina izquierda trasera
module atrapa_gt2 () 
{
    translate ([-despl_sop_guia_x,-sop_guia_y/2,pos_z_atrapa_gt2]) cube([x_bl_atrapa_gt2, largo_bl_atrapa_gt2, alto_bl_atrapa_gt2]);
}

// ---------------------- Bloques que atrapan la correa ----------------------

// El hueco para poner estos bloques
// Este hueco por ahora no se usa
y_hueco_atrapa_gt2 = sop_guia_y/2 - y_dist_seb/2 - cabeza_m3_r - 5; 
y_hueco_atrapa_gt2_mn = y_hueco_atrapa_gt2 + 1; // +1 para evitar non+manifold

// Dejar 1.5 a cada lado, ya que la correa es de 1.38 de grosor
radio_atrapa_gt2_gr = (sop_guia_x - 3) / 2;
// el del cilindro pequeno
radio_atrapa_gt2_pq = 1;

distancia_bloque_atrapa_cilindro = 4 + radio_atrapa_gt2_pq;

module rodea_gt2 () 
{
  hull () {
  // El cilindro para que la correa le rodee
  // La x la pongo a cero porque con la rotacion se queda descuadrada, y la muevo luego
  translate ([0,
              -sop_guia_y/2+largo_bl_atrapa_gt2+radio_atrapa_gt2_gr*2+distancia_bloque_atrapa_cilindro,
               pos_z_atrapa_gt2])
    cylinder (r=radio_atrapa_gt2_gr, h=alto_bl_atrapa_gt2,$fa=1, $fs=0.5);

  // El cilindro pequeno
  translate ([0,
              -sop_guia_y/2+largo_bl_atrapa_gt2+distancia_bloque_atrapa_cilindro,
              pos_z_atrapa_gt2])
     cylinder (r=radio_atrapa_gt2_pq, h=alto_bl_atrapa_gt2,$fa=1, $fs=0.5);
  }
}




difference () {
  union () {
    translate([-despl_sop_guia_x, -sop_guia_y/2,0])
      cube([sop_guia_x, sop_guia_y, sop_guia_z]);
    translate ([-despl_sop_guia_x+sop_guia_x/2,0,0]) rodea_gt2 ();
    translate ([-despl_sop_guia_x+sop_guia_x/2,0,0]) rotate ([0,0,180]) rodea_gt2();
      // Los bloques paralaleos que atrapan la correa
    atrapa_gt2();
    translate ([sop_guia_x-x_bl_atrapa_gt2,0,0]) atrapa_gt2();
    translate ([0,sop_guia_y-largo_bl_atrapa_gt2,0]) atrapa_gt2();
    translate ([sop_guia_x-x_bl_atrapa_gt2,sop_guia_y-largo_bl_atrapa_gt2,0]) atrapa_gt2();
  }

// Cubo que hace el hueco para que vayan las atrapa guias
//translate ([-despl_sop_guia_x-1,-sop_guia_y/2-1,pos_z_atrapa_gt2]) cube([sop_guia_x+2, y_hueco_atrapa_gt2_mn, alto_bl_atrapa_gt2+1]);
//translate ([-despl_sop_guia_x-1,sop_guia_y/2-y_hueco_atrapa_gt2_mn+1,pos_z_atrapa_gt2]) cube([sop_guia_x+2, y_hueco_atrapa_gt2_mn, alto_bl_atrapa_gt2+1]);
    
// La siguiente linea de huecos de la posicionadora Thorlabs esta 12.5
top_hole_thorlabs_z = 12.5;
tornillo (m4_r, cabeza_m4_r);
// Taladros de Thorlabs
translate([0,25,0]) tornillo(m4_r, cabeza_m4_r);
translate([0,-25,0]) tornillo(m4_r, cabeza_m4_r);
translate([0,12.5,top_hole_thorlabs_z]) tornillo(m4_r, cabeza_m4_r);
translate([0,-12.5,top_hole_thorlabs_z]) tornillo(m4_r, cabeza_m4_r);

// Taladros de NB SEBS15A y SEBLV16 (Misumi)
translate([0,10,0]) tornillo(m3_r, cabeza_m3_r);
translate([0,-10,0]) tornillo(m3_r, cabeza_m3_r);
// Estos estan unidos, asi que hago las cabezas y los vastagos separados
//translate([0,10,25]) tornillo(m3_r, cabeza_m3_r);
//translate([0,-10,25]) tornillo(m3_r, cabeza_m3_r);
//translate([0,10,top_hole_mgn12h]) tornillo(m3_r, cabeza_m3_r);
//translate([0,-10,top_hole_mgn12h]) tornillo(m3_r, cabeza_m3_r);

// Cabezas y vastagos separados:
translate([0,y_dist_seb/2,top_hole_seb]) vastago_tornillo(m3_r);
translate([0,-y_dist_seb/2,top_hole_seb]) vastago_tornillo(m3_r);
translate([0,y_dist_seb/2,top_hole_mgn12h]) vastago_tornillo(m3_r);
translate([0,-y_dist_seb/2,top_hole_mgn12h]) vastago_tornillo(m3_r);
hull () {
  translate([0,y_dist_seb/2,top_hole_seb]) cabeza_tornillo(cabeza_m3_r);
  translate([0,y_dist_seb/2,top_hole_mgn12h]) cabeza_tornillo(cabeza_m3_r);
}
hull () {
  translate([0,-y_dist_seb/2,top_hole_seb]) cabeza_tornillo(cabeza_m3_r);
  translate([0,-y_dist_seb/2,top_hole_mgn12h]) cabeza_tornillo(cabeza_m3_r);
   
}


// Los redondeos de las esquinas
translate([-despl_sop_guia_x, sop_guia_y/2,0]) redondeo_mxy(r_fillet=2, h_fillet= pos_z_atrapa_gt2+alto_bl_atrapa_gt2);
translate([-despl_sop_guia_x, -sop_guia_y/2,0]) redondeo_mxmy(r_fillet=2, h_fillet= pos_z_atrapa_gt2+alto_bl_atrapa_gt2);

}



translate ([sop_guia_x-despl_sop_guia_x,-base_filtro_y/2,base_filtro_z]) chaflan_hal (diagonal = 2, largo= base_filtro_y);

