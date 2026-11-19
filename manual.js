// ═══════════════════════════════════════════════════════════════════════
//  CRM Adorno · manual.js — Manual de uso (overlay 📖, autoinyectable)
//  🚨 REGLA: cada vez que se agrega o cambia una función del módulo,
//  actualizar la sección correspondiente acá (y bump del ?v= en index.html).
// ═══════════════════════════════════════════════════════════════════════

function _mEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function _manualSecciones() {
  const admin = (typeof session !== 'undefined') && session?.isAdmin;

  const base = [
    { icon: '🧭', titulo: 'La barra de arriba', desc: 'Es igual en todos los módulos: mismo lugar para cada cosa y el color de la moneda del módulo (el mismo del Hub).',
      pasos: ['A la izquierda, la moneda y el nombre del módulo, con tu local y tu nombre al lado. En la computadora, tocando el nombre (Clientes ▾) se abre la lista para pasar a otro módulo; al final de esa lista está «Volver al Hub».', 'Al lado van las pestañas (Nuevo, Pedidos, WhatsApp, Satisfacción, Clientes): son íconos; al pasar el mouse aparece el nombre, y la pestaña en la que estás queda marcada en blanco con su nombre. Cuando hay alertas, Pedidos se pone verde con el número.', 'A la derecha: el número de versión (si se pone amarillo, «Actualizar a vN», tocalo para cargar la nueva), 🔍 Buscar y 🔄 Actualizar.', 'En el celular: las pestañas, Buscar y Actualizar (si Pedidos tiene alertas, el ☰ muestra un puntito verde) están adentro del botón ☰; a la vista queda 🏠 Hub (volver al Hub).', 'Para cerrar la sesión: volvé al Hub y tocá 👤 (arriba) → Salir; se cierra en todos los módulos. En los módulos no hay botón de Salir.', '¿Dudas? Preguntale a Clodi (el botón de abajo a la derecha): sabe todo lo que dice este manual.', 'Para hablarle a Clodi (desde el 15-nov-2026): mantené apretado el micrófono (con el dedo, el mouse o la barra espaciadora) mientras hablás; aunque hagas pausas no se corta. Al soltarlo, la pregunta se manda sola. Si lo tocás y soltás enseguida, no manda nada; si no te escuchó, te avisa. En el iPhone y el iPad (desde el 18-nov-2026) el micrófono abre el teclado: se dicta con el 🎤 del teclado y se manda con retorno.', 'Avisos de error (desde el 16-nov-2026): cuando algo falla (no se pudo guardar, no hay conexión, venció la sesión, falta un permiso) aparece arriba un cartel rojo que NO se cierra solo: lo leés y lo cerrás con la ✕. Está en castellano simple; si hace falta mostrarle a JP qué pasó, tocá «Ver detalle técnico (para soporte)». Si el mismo aviso se repite, se cuenta (×2, ×3). Desde el 16-nov también quedan fijos hasta tocar la ✕ los avisos de datos que faltan o están mal («Falta el celular», «Elegí una vendedora») y los de «🔒 No tenés permiso». Solo los avisos de que algo salió bien («Guardado», «Enviado») o de información se cierran solos.'] },
    {
      icon: '🔐', titulo: 'Entrar una sola vez',
      desc: 'La sesión se comparte entre todos los módulos del sistema.',
      pasos: [
        'En el Hub, con el ícono 👤 de arriba, ingresás con tu usuario y podés tildar "Confiar en esta computadora".',
        'Con eso tildado, entrás a todos los módulos de ese equipo sin volver a escribir la clave.',
        'En las computadoras de los locales, que usan varias personas, NO se tilda: cada módulo sigue pidiendo usuario y contraseña por separado.',
        'La sesión se cierra desde el Hub (👤 → Salir) y se cierra en todos los módulos. La computadora sigue marcada como de confianza hasta que lo apagues desde el Hub.',
        'Desde el 16-nov-2026, Clientes usa directamente la sesión del Hub de los administradores (no guarda una copia aparte): así abrir Clientes ya no puede cortar la sesión en los demás módulos. El botón Salir de Clientes, con esa sesión, cierra la sesión en todo el sistema (igual que Salir en el Hub).',
      ],
    },
    {
      icon: '🏢', titulo: 'La Oficina',
      desc: 'La Oficina entra con cualquiera de sus dos cuentas y puede mirar lo de todos los locales, pero solo opera como Oficina.',
      pasos: [
        'Para entrar: elegí Oficina, tocá tu cuenta (administracion@ en la PC de Marisa, claudiaadorno@ en la de Analía) y poné la contraseña. La PC se acuerda de la cuenta para la próxima vez.',
        'Desde la Oficina se VE todo: los pedidos, la satisfacción, los clientes y el WhatsApp de Unicenter y de Alcorta.',
        'Lo que NO se hace desde la Oficina es operar en nombre de un local: no se cargan ni se cambian pedidos de un local y no se les responde a sus clientes. Eso lo hacen las chicas de cada local. El sistema lo frena aunque se intente.',
        'Como Oficina sí se opera: los pedidos de la Oficina (venta online) se cargan, se avisan y se cambian como siempre.',
        'En Pedidos, arriba aparece "Pedidos de: Oficina · Unicenter · Alcorta · Todos los locales". En Oficina están los tuyos, con sus botones y sus alertas. Si elegís otro local ves sus pedidos sin botones (dice "Solo para mirar"); para volver a operar, tocá Oficina.',
        'En WhatsApp ves las charlas de todos los locales (arriba elegís cuál). Abajo de la charla de un local dice "desde acá se mira, no se responde", y abrirla no la marca como leída para las chicas del local. El número verde de la pestaña y los avisos son solo de lo que le toca a la Oficina.',
        'En Clientes ves los clientes de todos los locales, no solo los que compran en la Oficina. Satisfacción muestra las encuestas de todos los locales.',
        'La pestaña Admin sigue siendo solo de los administradores.',
        'Desde el 14-nov-2026, ver y operar otros locales sale del Hub (ver «Permisos del Hub»). Si JP deja «Ver pedidos y charlas de los otros locales» en Pide permiso, al elegir otro local en «Pedidos de:» aparece la ventana de autorización del Hub: lo autoriza alguien que lo tenga habilitado (hoy, un dueño) con la cara, desde el celu o con su clave, y vale hasta que volvés a Oficina.',
      ],
    },
    {
      icon: '🔑', titulo: 'Permisos del Hub',
      desc: 'Desde el 14-nov-2026, lo que cada cuenta puede hacer en Clientes lo maneja JP en el Hub → 👤 → Permisos. Cada función está Habilitada, Pide permiso u Oculta.',
      pasos: [
        'Habilitada: se usa como siempre.',
        'Oculta: no aparece. Si es una pestaña (Nuevo, Pedidos, WhatsApp, Clientes, Satisfacción), no se ve. Si es un botón (cambiar el estado, avisar, editar, borrar, responder por WhatsApp, etiquetas de la ficha, datos sacados de los chats), no está: la tarjeta o la charla se ve igual, para mirar.',
        'Pide permiso: se ve, pero al usarla aparece la ventana «Esto necesita autorización» del Hub (desde el 15-nov-2026, la misma en todos los módulos). Primero la cámara lee en segundo plano (no se ve la imagen, solo «Verificando…»): si quien puede autorizarlo está mirando a la compu, aparece «Autorizado por …» y listo. Si no está o no anda la cámara, tocás «📱 Pedir al celu o con clave»: aparece la lista de quienes pueden autorizar (primero los que están en el local según el reloj) y con «📱 Pedir a…» le llega un aviso al celular para Aceptar o Rechazar (se espera hasta 3 minutos). Si no tiene el celular a mano, pone ahí mismo su mail y su clave personales.',
        'Autoriza quien tiene esa función habilitada en el Hub y ese local (en Clientes, las encargadas con su legajo) o un dueño. Nunca la cuenta del local o de la oficina, ni uno mismo. Cada autorización sirve para UNA sola operación (lo decidió JP el 15-nov-2026, igual que en Tesorería): ese pedido, esa charla, esa ficha o esa sugerencia; al cargar un pedido, esos artículos; al analizar chats, esos archivos. Para otra cosa hay que pedirla de nuevo. Vence a los 10 minutos si no se usa. La operación queda hecha con la cuenta del local (no hace falta que quien autoriza abra su sesión) y en el Hub queda quién autorizó, cómo (cara, celu o clave) y para qué.',
        'Si es algo de mirar (una pestaña, o los pedidos de otro local), se autoriza al entrar y vale hasta que cambiás de pestaña o volvés a tu local.',
        'Al cargar o editar un pedido, el permiso se pide recién al tocar Guardar, cuando el formulario ya está completo.',
        'Borrar un pedido: lo autoriza la encargada del local o un administrador (con la misma ventana), y además tiene que tener «Borrar un pedido» habilitado en el Hub.',
        'Si tu usuario tiene varios locales en el Hub, al entrar te pregunta en cuál estás trabajando. Lo cambiás tocando el nombre del local, arriba.',
        'Ver y operar en otros locales también sale del Hub. Hoy la Oficina ve todo y opera solo como Oficina (ver «La Oficina»).',
        'El sistema lo controla también por detrás: aunque alguien quiera saltearse la pantalla, la base no deja grabar lo que esa cuenta no tiene habilitado. Lo mismo al mandar un WhatsApp.',
        'La pestaña Admin (estadísticas, bot, números) sigue siendo solo de los administradores. Adentro, «Analizar» y «Generar ahora» de Chats tienen su propio permiso porque gastan IA.',
        'Apartados (desde el 15-nov-2026): en Hub → Permisos → Perfiles, JP puede apagar un apartado entero de Clientes para un perfil: Clientas, Pedidos, WhatsApp, Otros locales o Administración. Lo de ese apartado queda Oculto para ese perfil.',
        'Dueños con «vista» (hoy Clau): siguen siendo administradores y pueden hacer y autorizar todo, pero en Clientes ven solo los apartados que JP les deja prendidos. Se esconden las pestañas y, dentro de Admin, las vistas de esos apartados: Resumen y Métricas son de Administración; Clientes 360° y Cumpleaños, de Clientas; Bot WhatsApp, de WhatsApp; Chats y Números, de Administración. Si no le queda ninguna vista, la pestaña Admin no aparece. JP ve todo, como siempre.',
        '«Ver como» (desde el 16-nov-2026, solo JP): desde el Hub, JP puede entrar a Clientes viendo lo que ve otra cuenta, para revisar qué ve y qué permisos tiene. Es SOLO PARA MIRAR: arriba aparece el cartel «Viendo como … · solo lectura» con el botón Salir. No se graba nada, no se piden permisos ni quién lo hace, no sale ningún WhatsApp (ni por el número del sistema ni abriendo WhatsApp o el mail) y no se marcan charlas como leídas. Al tocar algo que grabaría: si esa cuenta lo tiene Habilitado, lo avisa; si le pediría permiso, se abre igual la ventana de autorización del Hub, en solo lectura, con la lista real de quién podría autorizarlo (sin cámara: «Pedir a…» y «Autorizar con clave» solo muestran un cartel) y, al cerrarla, no se hace nada. Clodi, las fotos de las charlas y el estado de los números (Admin › Números) no cargan en ese modo. «Salir» vuelve al Hub con la cuenta de JP.',
        'Si un día el Hub no contesta, Clientes sigue funcionando como antes del 14-nov y la base sigue controlando.',
      ],
    },
    {
      icon: '📷', titulo: 'Registra quién lo hizo',
      desc: 'Desde el 14-nov-2026 JP puede marcar en el Hub qué funciones de Clientes anotan quién las hizo.',
      pasos: [
        'Si JP marcó una función con 📷 Registra quién en el Hub, al usarla se pide quién la está haciendo (por la cara, o tocando tu nombre en la lista); con usuario personal se anota solo.',
        'Desde el 15-nov-2026 el reconocimiento por cara está prendido: con la cuenta del local la cámara te lee la cara en segundo plano, sin abrir ninguna ventana (avisa «Anotado: …») y sigue sola. Si no te reconoce o todavía no tenés la cara grabada, aparece la lista con los nombres de la gente del local: tocás el tuyo y sigue. Si venís de otro local, tocá «Ver todos los locales». En las compus que tienen el fichador por cámara (desde el 16-nov-2026): cuando el sistema necesita la cámara para ver quién sos o para autorizar, le pide al fichador que la suelte un momento y después se la devuelve sola; tarda uno o dos segundos más. Si igual dice que la cámara está ocupada, pausá el fichador desde su ícono al lado del reloj y probá de nuevo.',
        'Si cerrás esa ventana o tocás Cancelar, la operación no se hace: no se carga, no se cambia y no se manda nada.',
        'Puede pasar en: cargar un pedido; cambiar su estado, marcarlo listo, avisar a la clienta (por el número del local o con un mensaje armado), editarlo y borrarlo; responder por WhatsApp, descartar una sugerencia del bot o pausarlo; corregir la ficha de una clienta (etiquetas, celular); aceptar o rechazar los datos sacados de los chats; y, en Admin, configurar el bot, aplicar el nombre nuevo de un número (Admin › Números, con el PIN), conectar el número de siempre de un local, analizar chats exportados y generar el informe en el momento (Admin › Chats). Lo de Admin lo usa un administrador con su usuario, así que se anota solo, sin ventana (el PIN nunca queda en el registro).',
        'En WhatsApp no se pregunta dos veces: queda anotada la persona de «¿Quién responde?» (si la reconoció la cámara, queda «📷 por la cara»). Lo mismo al cargar un pedido desde una charla. Si te pregunta en otro paso (por ejemplo al responder desde la tarjeta del pedido), quedás como «¿Quién responde?» los 10 minutos.',
        'Para no llenar el registro, si la misma persona responde varios mensajes en la misma charla, se anota una vez cada 10 minutos.',
        'Al borrar un pedido, primero autoriza la encargada o un administrador y después se anota quién lo está borrando. Lo mismo con cualquier función que esté en «Pide permiso»: se anota a quien la usa, después de que autorizaron.',
        'La foto nunca se guarda: queda solo quién fue, cuándo, con qué cuenta y qué hizo. JP lo ve en el Hub → Permisos → Registro.',
      ],
    },
    {
      icon: '🧭', titulo: 'Cómo se navega',
      desc: 'La barra de arriba tiene, en orden, Nuevo pedido, Pedidos (con las Alertas arriba de todo) y WhatsApp (y Satisfacción).',
      pasos: [
        'Al entrar, el CRM abre directo en Nuevo pedido, que es lo que más se usa.',
        'Cuando hay algo para hacer, la pestaña Pedidos se pone toda en verde con el número de alertas. Si está gris, no hay nada. Ese mismo número aparece en rojo sobre el ícono de la ventana en la barra de tareas (y en el ícono de la app en el celular), aunque la tengas minimizada.',
        'Desde el 4-nov-2026 Alertas ya no es una pestaña aparte: está arriba de todo dentro de Pedidos. La pestaña Hoy tampoco existe (26-oct-2026).',
        'Los botones tienen movimiento: al tocarlos rebotan y sale una onda desde donde tocaste, así te das cuenta de que tomó el toque. Con el mouse, además, se agrandan un poco al pasar por encima. En las alertas, el botón principal late suave para que se vea qué conviene hacer.',
      ],
    },
    {
      icon: '➕', titulo: 'Nuevo pedido',
      desc: 'Cargar el encargo de una clienta cuando no hay stock o hay que traerlo.',
      pasos: [
        'Quién lo carga (desde el 19-nov-2026): ya no se elige la vendedora. Al tocar «Guardar pedido», la cámara te reconoce en segundo plano (aparece «Un momento…» y después tu nombre) y el pedido queda a tu nombre. Si no te reconoce o no hay cámara, tocás tu nombre en la lista; si venís de otro local, «Ver todos los locales». Si entraste con tu usuario, queda a tu nombre sin cámara. Cada pedido se reconoce de nuevo: si el siguiente lo carga otra persona, queda a nombre de ella.',
        'Cargá el DNI o CUIT: si la clienta ya compró alguna vez, el sistema la detecta solo y completa sus datos.',
        'El celular cargalo con la característica: 11 y los 8 números (sin el 0 ni el 15). Si lo ponés como 15 + 8 números, o solo los 8, el sistema le agrega el 11 solo al salir del casillero: es de Buenos Aires. Si es de otra ciudad, poné su característica.',
        'Agregá los artículos buscando por descripción o SKU. Al lado de cada código ves el stock vivo de cada local: A = Alcorta, U = Unicenter, O = Oficina (verde si hay).',
        'Anotá seña si dejó, y cualquier aclaración en las notas.',
        'El pedido arranca en estado "Pendiente".',
        'Al guardar, a la clienta le llega la confirmación del pedido ("registramos tu pedido de…, te avisamos apenas esté disponible"). Si tu local tiene el WhatsApp conectado al sistema, sale sola desde el número del sistema (no se abre tu WhatsApp) y ves "Confirmación enviada"; si algo falla, te ofrece mandarla desde el WhatsApp del local. Si tu local no está conectado, se abre el WhatsApp del local con el mensaje escrito, como siempre.',
        'Los mensajes de WhatsApp que arma el sistema (la confirmación del pedido y el aviso de que llegó) usan el primer nombre de la clienta con mayúscula inicial ("Hola Karina!", no "Hola KARINA!") y el artículo en minúscula y con tildes ("el juego de sábanas Paris queen"), aunque en el sistema esté todo en mayúsculas. Si escribiste la descripción a mano, sale tal cual.',
        'Si tu local tiene el WhatsApp conectado al sistema, vas a ver el botón verde "Enviar aviso": manda el mensaje desde el número del local y marca Avisado solo. Cuando el cliente responde, el pedido pasa a "Respondió" automáticamente y ves su mensaje en la tarjeta, junto con ✓✓ entregado / leído.',
        'Con el aviso mandado por el sistema, vos solo cargás el pedido y mandás el primer aviso: lo demás es automático. Si la clienta contesta, pasa a Respondió. Si no contesta, a las 48 horas le llega un recontacto, 48 horas después otro y, si sigue sin contestar 48 horas más, el pedido pasa a No contestó. Los recontactos salen entre las 10 y las 20, nunca de noche. Ya no hace falta cargar si respondió.',
        'Si el DNI no tenía ficha, el pedido muestra "⏳ Dragon": el cliente se da de alta solo en Dragonfish desde Oficina (cada 15 min) y pasa a "✔ Dragon". No hace falta cargarlo a mano.',
      ],
    },
    {
      icon: '📦', titulo: 'Pedidos',
      desc: 'Arriba, las Alertas en verde; abajo, el listado del resto de los pedidos con el circuito de estados.',
      pasos: [
        'Si hay alertas, arriba de todo aparece la barra verde "Alertas" con el número y abajo sus tarjetas (ver Alertas). Debajo dice "Los demás pedidos": ahí están los filtros y el resto. Un pedido que tiene una alerta se ve solo arriba; si el filtro elegido tiene alguno, te lo avisa ("1 pedido de este filtro está arriba, en Alertas").',
        'Cuando abrís el chat de WhatsApp de un pedido Avisado y volvés al CRM, aparece abajo "¿Respondió?": tocás Sí, No o Después y listo. No hace falta entrar al pedido para cargar la respuesta.',
        'El circuito es: Pendiente → Listo para avisar → Avisado → Respondió / No contestó → Completado o Cancelado.',
        'Para corregir un pedido tocá el lápiz ✎ de la tarjeta. Abajo de todo está "🗑 Eliminar pedido": borrar un pedido lo autoriza la encargada del local o un administrador. Desde el 15-nov-2026 se abre la ventana de autorización del Hub: la encargada mira a la cámara, o le llega un aviso al celular para aceptar, o pone ahí su mail y su clave personales (ver «Permisos del Hub»). La cuenta del local o de la oficina no alcanza, y la encargada de otro local tampoco; además tiene que tener «Borrar un pedido» habilitado en el Hub. Esa ventana ya es la confirmación: el pedido se borra definitivamente y en el historial queda quién lo autorizó. Un administrador (o la encargada entrando con su usuario) lo borra directo, con dos confirmaciones.',
        'Los botones de cada pedido son solo íconos: dejá el mouse encima (o mantené apretado en el celular) y te dice qué hace. El más grande y de color es la acción principal de ese estado: avisar, marcar que respondió o que ya retiró. El verde siempre es WhatsApp.',
        'Cuando llega la mercadería, pasá el pedido a "Listo para avisar".',
        'El botón de WhatsApp arma el mensaje solo, con la plantilla que corresponde al estado.',
        'En las PC de los locales, el botón de WhatsApp abre el chat directo en la ventana de WhatsApp del kiosco (la que ya tiene la sesión), con el mensaje ya escrito: no abre ventanas nuevas ni pide QR. La primera vez Edge pregunta si abre la aplicación: tildá "Permitir siempre".',
        'Al avisar, marcá "Avisado" — si en 60 minutos no hay respuesta, el sistema te lo recuerda solo.',
        'Filtrá por vendedora, estado o etiquetas para encontrar rápido lo que buscás.',
        'Si el local tiene el WhatsApp conectado, en la tarjeta aparece "💬 WhatsApp" con toda la conversación: tocalo para abrirla. Mientras el cliente escribió en las últimas 24 h podés contestarle ahí mismo desde el número del local (Ctrl+Enter envía). Pasadas las 24 h solo se puede mandar la plantilla de recontacto.',
        '¿Quién responde? (desde el 13-nov-2026): como la compu entra con el usuario del local, la primera vez que mandás un mensaje por WhatsApp el sistema pregunta quién sos. Desde el 15-nov-2026 la cámara te lee la cara en segundo plano, sin abrir ninguna ventana: aparece «Un momento…» y después «Responde: Soraya» (hay que tener la cara grabada en el Hub). Si en unos segundos no te reconoce o no hay cámara, elegís tu nombre de la lista del equipo (con un puntito verde las que están en el local ahora). Tu nombre sale como te conocen todos, el mismo que en los pedidos (desde el 19-nov-2026), aunque en el legajo figure primero otro nombre. Queda 10 minutos: abajo de la charla dice "Respondés como Soraya (8 min más) · Cambiar". Los mensajes salen firmados con tu nombre y la charla queda "la sigue Soraya".',
        'Cuando Clodi pasa una consulta al local, en la charla aparece el botón "🙋 Tomar la consulta". Al tocarlo te pregunta quién sos (cara o lista) y le manda solo a la clienta un saludo: "¡Hola! Soy Soraya, de Claudia Adorno Unicenter. Ya vi tu consulta y te sigo yo por acá 🙂". Después aparece el cuadro para escribirle vos; Clodi se queda callado en esa charla.',
        'Si el bot del local está en "Sugiere respuestas", cuando el cliente escribe te deja una "respuesta sugerida" en la tarjeta y en Alertas: ✓ la mandás tal cual, ✎ la corregís antes de mandarla o ✗ la descartás; nada sale sin que alguien lo apruebe. Si está en "Responde solo", el bot (Clodi, la asistente virtual) contesta directo y vos ves toda la charla en "💬 WhatsApp".',
        'Cuando la clienta necesita a una persona (lo pide, tiene una queja o un cambio, quiere reservar, o el bot no sabe la respuesta), el bot le avisa "dame un segundo que busco a alguno de los chicos del local" (si el local está cerrado, que le escriben apenas abra) y a las que están trabajando en el local en ese momento (según las fichadas del reloj) y a la encargada les llega al celular la notificación "💬 Nombre necesita una persona", que abre la charla directo. Contestale vos desde la pestaña WhatsApp. Si nadie del local le escribe en 3 horas, el bot la vuelve a atender solo (y le pide disculpas si reclama).',
        'Lo que el bot nunca hace: decir precios (pasa el link de la web, ahí está el precio), ofrecer reservar o guardar un producto (si la clienta lo pide, le cuenta lo de la seña y te la pasa) ni confirmar stock sin mirar el sistema (dice "según el sistema hoy lo tenemos", le ofrece que ustedes lo confirmen y la invita a pasar por el local). Audios, videos y archivos no los puede ver: te los pasa. Si un mensaje le llega cortado (a veces WhatsApp no lo entrega), le pide a la clienta que lo mande de nuevo; si le vuelve a pasar, te la pasa. Si una clienta dice que algo llegó roto o con un defecto, le pide una foto o un video del daño y la foto del ticket o la factura, y te pasa la charla; cuando llega ese video, le agradece y te la pasa (no le dice que no lo puede ver). Nombre, apellido y DNI los pide solo cuando la clienta quiere comprar, encargar o reservar algo, pregunta por un pedido suyo o tiene una queja; por una consulta que no sabe responder, no.',
        'Si la clienta pregunta por algo que hoy no hay en el local, el bot le ofrece anotarla y, si dice que sí, carga solo el pedido "Avisar cuando ingrese" a su nombre (vendedora "Clodi (WhatsApp)") y te llega la notificación "🆕 Clodi anotó un pedido". Revisalo como cualquier pedido: si en la nota dice "completar DNI" o "sin código de Dragonfish", completalo vos. Cuando llega la mercadería se avisa igual que siempre.',
        'El bot sabe quién está trabajando ahora en el local (por el reloj de fichadas y los turnos). Si la clienta pregunta "¿está Soraya?", le dice si está o no (sin dar horarios). Si pide que la atienda una vendedora en particular, el aviso le llega solo a esa vendedora ("💬 … quiere que la atiendas vos"); si esa vendedora no está ahora, le llega igual y también al local, para que alguien la atienda. Si pregunta por alguien que no trabaja en ese local, le dice que no la ubica en el equipo (capaz la atendió en el otro local) y le ofrece que la ayude alguno de los chicos. Si una clienta felicita a alguien del equipo, Clodi le agradece y le hace llegar el mensaje a esa persona (le llega el aviso a ella).',
        'Otras cosas del bot: si preguntan por envíos o compras online, le pasa el WhatsApp de administración (no te la pasa a vos). Si la clienta pregunta si le guardan un pedido que ya llegó, no le habla de seña (no es una reserva): te la pasa para que le confirmes hasta cuándo. Si no está exactamente lo que busca, le ofrece lo más parecido de la web antes de pasártela (por ejemplo, para algo con aroma, la línea Spa).',
        'Si aprobás o corregís la sugerencia, el bot sigue atendiendo esa conversación. Si escribís vos un mensaje propio, el bot se corre durante 12 horas para no pisarte; con el ✓ del recuadro "bot en pausa" se lo devolvés antes.',
      ],
    },
    {
      icon: '💬', titulo: 'WhatsApp',
      desc: 'Todas las charlas del número del local en el sistema (el del bot), tengan o no un pedido. Funciona como el WhatsApp Web.',
      pasos: [
        'A la izquierda está la lista de charlas, la más nueva arriba. El número verde son los mensajes que nadie del local leyó todavía. Las que necesitan a una persona aparecen primero y con la cara en amarillo: "para atender", "sugerencia" (el bot dejó una respuesta para aprobar) o "pasada al local" (el bot la derivó).',
        'Cuando hay una charla para atender, la pestaña WhatsApp se pone verde con el número (cuenta las de las últimas 24 horas) y suma en el número rojo del ícono de la ventana. Arriba de la lista podés filtrar Todas, Para atender o Sin leer, y buscar por nombre o celular.',
        'Aviso cuando entra una charla para atender: en la PC del local suena un aviso y sale un cartel abajo, aunque estés en otra pestaña del CRM. Si tocás "🔔 Activar avisos en esta PC" (arriba de la lista, una sola vez por PC) y le das Permitir, también aparece la notificación de Windows aunque el CRM esté minimizado; tocándola se abre la charla.',
        'Al celular les llega la notificación a las que están trabajando en el local en ese momento (el sistema lo sabe por las fichadas del reloj, y si todavía no fichó, por el turno) y a la encargada. Para recibirla hay que tener activadas las notificaciones en RRHH, Stock o Ventas. Tocándola se abre la charla directo.',
        'Tocá una charla para verla entera: lo que escribió la clienta (blanco), lo que contestó Clodi, el bot (violeta), y lo que mandaron ustedes (verde), con ✓ enviado, ✓✓ entregado y ✓✓ leído.',
        'Para contestar escribí abajo y apretá Enter (Shift+Enter para bajar de renglón). Sale desde el número del local. WhatsApp solo deja escribir libre hasta 24 horas después del último mensaje de la clienta; pasado ese tiempo el cuadro se cierra hasta que ella vuelva a escribir.',
        'Si hay una respuesta sugerida por el bot: ✓ la mandás tal cual, ✎ la corregís en el cuadro antes de mandarla o ✗ la descartás.',
        'Si la clienta te encarga algo, tocá el botón de pedido que está a la izquierda del cuadro de escribir: se abre Nuevo pedido encima de la charla con sus datos ya cargados (nombre, DNI, celular y mail, si los tenemos). Elegís el artículo y guardás: el pedido queda a nombre de quien responde la charla (si todavía no hay nadie, te reconoce la cámara o elegís tu nombre, y quedás respondiendo la charla). El pedido queda en el local de la charla y en el cuadro queda escrita la confirmación para la clienta: revisala y mandala con Enter. Con la ✗ de arriba cerrás sin guardar.',
        'Arriba a la derecha de la charla ves qué hace el bot ahí: con ✗ lo pausás y la seguís vos; con ✓ se la devolvés al bot. Si escribís un mensaje propio, el bot se corre solo durante 12 horas.',
        'Si la clienta manda varios mensajes seguidos (por ejemplo "hola", "estoy en Neuquén", "hacen envíos?"), Clodi espera unos segundos a que termine de escribir y le contesta una sola vez a todo junto. Por eso a veces la respuesta tarda unos 10 segundos más.',
        'Las fotos que manda la clienta se ven en la charla (tocala para agrandarla). Los audios, videos y archivos se abren al tocarlos. WhatsApp guarda esos archivos unos 30 días.',
        'Si la clienta reacciona a un mensaje con un emoji (👍, ❤️), el emoji aparece abajo de ese mensaje, como en WhatsApp, y en la lista dice "Reaccionó 👍". Una reacción sola no deja la charla "para atender" ni suma como mensaje sin leer.',
        'Al abrir una charla queda leída para todo el local. Si la abre alguien de la oficina, para ustedes sigue como nueva. Desde la Oficina se pueden mirar las charlas de los locales, pero no responderlas: eso lo hacen ustedes.',
        'Si tu local todavía usa el número +1 del sistema, acá están solo esas charlas; las del celular del local siguen en el WhatsApp de siempre. Cuando el local conecta su número de siempre (lo hace un administrador desde Admin › Bot WhatsApp), acá aparecen también las charlas del celular de los últimos 6 meses (sin los grupos), y lo que contestes desde el celular queda en la charla.',
        'Con el número de siempre conectado, el celular sigue funcionando igual. Si le contestás a una clienta desde el celular, Clodi se corre de esa charla durante 12 horas, igual que si le escribís desde acá. En la compu usá WhatsApp Web en el navegador: WhatsApp para Windows deja de andar con ese número.',
      ],
    },
    {
      icon: '👥', titulo: 'Clientes',
      desc: 'La base de clientas: datos, historial de compras y etiquetas.',
      pasos: [
        'Buscá por nombre, DNI o CUIT — están todas las clientas de Dragonfish.',
        'La ficha muestra el historial completo de compras y los pedidos que hizo.',
        'Podés ponerle etiquetas (tags) para agruparlas y filtrarlas después.',
        'En la ficha aparece "💬 Lo que sabemos por WhatsApp": lo que le gusta, los productos que pidió (marcados los que no había), fechas que mencionó (cumpleaños, eventos) y un resumen de las últimas charlas. Sale solo de los chats analizados.',
      ],
    },
    {
      icon: '⏰', titulo: 'Alertas',
      desc: 'Todos los pedidos que están esperando una acción tuya. Están arriba de todo en la pestaña Pedidos.',
      pasos: [
        'Primero aparecen siempre los artículos que ya llegaron y hay que avisar; abajo, los pedidos avisados hace más de una hora que esperan que cargues si el cliente respondió. Cuando los avisos salgan por la API, esa segunda parte se completa sola.',
        'Concentra los avisados sin respuesta (+60 min) y otros vencimientos.',
        'El numerito rojo del encabezado te dice cuántas alertas hay sin resolver.',
        'Abajo de todo, "🪪 Clientes con datos para confirmar": son datos que el cliente pasó por WhatsApp (DNI, mail, cumpleaños). Con ✓ los revisás, corregís si hace falta y confirmás: si es nuevo se da de alta en Dragonfish (lo sube la PC de Oficina cada 15 min); si ya era cliente se completa lo que le faltaba, sin pisar nada. Con ✗ los descartás. Nada se carga sin que una persona lo confirme.',
      ],
    },
    {
      icon: '⭐', titulo: 'Satisfacción',
      desc: 'Las encuestas que las clientas responden después de completar su pedido.',
      pasos: [
        'Cada pedido completado dispara una encuesta (Google Forms); las respuestas se ven acá.',
        'Sirve para ver cómo venimos en atención por local y por vendedora.',
      ],
    },
    {
      icon: '🔍', titulo: 'Buscador y ajustes',
      desc: 'Herramientas del encabezado, siempre a mano.',
      pasos: [
        'La lupa 🔍 (o Ctrl+B) busca en todo: clientes, pedidos, productos y facturas.',
        '🌙 cambia entre tema claro y oscuro.',
        '↻ actualiza los datos sin recargar la página.',
        'Arriba a la derecha está el número de versión del CRM (por ejemplo "v94"). Si se publicó una versión más nueva mientras tenías la página abierta, se pone amarillo y dice "Actualizar a v95": tocalo y el CRM se recarga con la nueva. Si algo no anda como te contaron, mirá primero ese número.',
      ],
    },
  ];

  if (admin) {
    base.push({
      icon: '🛠', titulo: 'Admin',
      desc: 'Panel de administración — solo JP.',
      pasos: [
        'Pestaña ⏱ Métricas: cuánto tardan las vendedoras en avisar desde que hay stock, cuánto en cargar la respuesta, cuántos pedidos quedan colgados y cuántos se completan. Por local, por vendedora y por mes; elegí el período arriba. Verde = bien, rojo = atrasado.',
        'Auditoría: registro de todos los cambios (quién tocó qué y cuándo).',
        'Demanda no satisfecha: qué pidieron las clientas que no teníamos — insumo para compras.',
        'Gestión de vendedoras, plantillas de WhatsApp y configuración general.',
        'Si tenés activado el código del celular, al entrar como administrador (con la clave o desde el Hub) el CRM te pide el código de 6 números de la app de autenticación, igual que los otros módulos. Sin el código no se puede usar Admin.',
        'Pestaña 🤖 Bot WhatsApp: prendé o apagá el bot de cada local. "Sugiere respuestas" deja que la vendedora apruebe cada mensaje; "Responde solo" contesta directo. Para probar, cargá tu celular en la lista: el bot te contesta solo a vos y al resto le sigue dejando sugerencias. No prende los avisos por API ni el recontacto automático.',
        'Conectar el número de siempre del local (en Bot WhatsApp): elegís el local y tocás "Conectar número". Se abre la ventana de Meta: con el celular del local a mano (WhatsApp Business actualizado) ponés el número, confirmás con el código que aparece en la app y elegís compartir el historial. El número de siempre pasa a ser el del local en el CRM y en Clodi, y el +1 queda libre. Las charlas de los últimos 6 meses van llegando en unos minutos (abajo del botón ves cómo va). Los avisos por API de ese local quedan apagados hasta que Meta apruebe las plantillas en el número nuevo y se cargue la forma de pago; mientras tanto los avisos salen como antes, desde el WhatsApp del local.',
        'Más abajo, en la misma pestaña, le enseñás al bot: "Cómo habla" (tono, largo, emojis) y "Preguntas frecuentes" (lo que puede contestar: reservas, cambios, medios de pago, envíos). Lo que no esté ahí, no lo inventa: lo pasa a una vendedora. Con "Probar el bot" ves qué contestaría antes de guardar. También aprende de cómo las vendedoras corrigen sus respuestas; si una corrección no te gusta, la sacás con ✗.',
        'Pestaña 💬 Chats: subí chats exportados del WhatsApp del local (en el chat: Exportar chat › Sin archivos; el .txt de Android o el .zip de iPhone, varios a la vez) y el sistema los analiza: resumen, gustos, productos pedidos y sin stock, y los datos del cliente para confirmar en Alertas. Más abajo está el informe mensual (se arma solo el día 1 de cada mes con el mes anterior; "Generar ahora" muestra el mes en curso) y la lista de conversaciones analizadas: tocá una para ver el detalle. Las charlas de los números del local se analizan solas 6 horas después de que quedan quietas.',
        '«Analizar» (chats exportados) y «Generar ahora» (informe) gastan IA, así que desde el 14-nov-2026 cada uno tiene su propio permiso en el Hub: «Subir chats exportados del celular y analizarlos con IA» y «Generar el informe mensual de WhatsApp en el momento». Si está Oculto, el botón no aparece; si Pide permiso, lo autoriza alguien que lo tenga habilitado, con la ventana de autorización del Hub (cara, aviso al celu o su clave); y si JP lo marcó con 📷, se anota quién lo hizo antes de llamar a la IA. El servidor también lo controla: aunque alguien quiera saltearse el botón, no se gasta IA sin el permiso. El informe automático del día 1 y el análisis solo de las charlas del número del local no dependen de esto.',
        'Cuando una clienta pregunta por un producto, el bot lo busca en la web y le manda la foto con el nombre y el link (ahí está el precio), y le dice si según el sistema hay en el local. Si pregunta medidas, material o color, los lee de la página del producto. Si hay muchos modelos, le pasa 2 o 3 y el link del buscador de la web para ver el resto. En "Web que usa el bot" elegís www.claudiaadorno.com o la tienda del Atelier (cuando esté abierta al público). Si la clienta manda una foto de un producto, el bot la compara con las fotos de la web y le pasa el link; si hay dos muy parecidos, le pasa los dos.',
        'El bot le pide a la clienta, una sola vez y sin insistir, nombre y apellido, DNI y mail para registrarla (si ya los tenemos, no los pide). No la da de alta: esos datos aparecen en Alertas › clientes con datos para confirmar, y ahí una vendedora los confirma.',
        'Al final de la pestaña, "🔒 Reglas fijas (no se cambian desde acá)" muestra lo que el bot nunca negocia: precios, stock, reservas, cuándo pasa la charla al local y cómo escribe. Si "Cómo habla" o las preguntas frecuentes dicen otra cosa, mandan esas reglas. El bot llama a la clienta por el primer nombre o su apodo (Florencia → Flor), saluda solo en el primer mensaje y usa el nombre poco: si ya la nombró en las últimas 3 horas, no lo repite.',
      ],
    });
  }
  return base;
}

function abrirManual() {
  if (document.getElementById('manual-overlay')) return;
  const items = _manualSecciones();
  const ov = document.createElement('div');
  ov.id = 'manual-overlay';
  ov.innerHTML = `
    <div class="m-box">
      <div class="m-head">
        <span style="font-size:22px;">📖</span>
        <div style="flex:1;">
          <div style="font-weight:700;font-size:16px;">Manual · Clientes</div>
          <div style="font-size:12px;opacity:.85;">Guía rápida de cada herramienta del módulo</div>
        </div>
        <button class="m-close" onclick="cerrarManual()">✕</button>
      </div>
      ${items.map((s, i) => `
        <div class="m-sec">
          <div class="m-tit">${s.icon} ${i + 1}. ${_mEsc(s.titulo)}</div>
          <div class="m-desc">${_mEsc(s.desc)}</div>
          <ul class="m-pasos">${s.pasos.map(p => `<li>${_mEsc(p)}</li>`).join('')}</ul>
        </div>`).join('')}
      <div class="m-foot">💡 Este manual se actualiza junto con el sistema. ¿Falta algo o no funciona? Avisale a JP.</div>
    </div>`;
  document.body.appendChild(ov);
  _manualLupa(ov);
  document.body.style.overflow = 'hidden';
}

function cerrarManual() {
  const ov = document.getElementById('manual-overlay');
  if (ov) ov.remove();
  document.body.style.overflow = '';
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarManual(); });

(function _manualInit() {
  const css = document.createElement('style');
  css.textContent = `
    #manual-overlay{position:fixed;inset:0;background:rgba(15,23,42,.55);z-index:9999;display:flex;align-items:flex-start;justify-content:center;padding:20px 12px;overflow-y:auto;-webkit-overflow-scrolling:touch;}
    #manual-overlay .m-box{background:#f8fafc;border-radius:14px;max-width:760px;width:100%;padding-bottom:6px;box-shadow:0 20px 60px rgba(0,0,0,.3);}
    #manual-overlay .m-head{position:sticky;top:0;background:#0f6e56;color:#fff;padding:14px 18px;border-radius:14px 14px 0 0;display:flex;align-items:center;gap:10px;z-index:1;}
    #manual-overlay .m-close{background:rgba(255,255,255,.18);border:none;color:#fff;font-size:16px;border-radius:8px;padding:6px 11px;cursor:pointer;}
    #manual-overlay .m-sec{background:#fff;border:1px solid #e2e8f0;border-left:4px solid #0f6e56;border-radius:10px;margin:14px 14px 0;padding:14px 18px;}
    #manual-overlay .m-tit{font-weight:700;font-size:15px;margin-bottom:4px;color:#064e3b;}
    #manual-overlay .m-desc{font-size:13px;color:#475569;margin-bottom:8px;}
    #manual-overlay .m-pasos{margin:0 0 2px 18px;padding:0;font-size:13px;line-height:1.65;color:#334155;}
    #manual-overlay .m-pasos li{margin-bottom:4px;}
    #manual-overlay .m-foot{margin:16px 14px 12px;background:#fef3c7;border-left:4px solid #d97706;border-radius:8px;padding:11px 14px;font-size:12.5px;color:#92400e;}`;
  document.head.appendChild(css);

  const hdr = document.querySelector('.header-right');
  if (hdr) {
    const b = document.createElement('button');
    b.className = 'hdr-ico';
    b.title = 'Manual de uso';
    b.setAttribute('aria-label', 'Manual');
    b.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5a2 2 0 0 1 2-2h6v16H6a2 2 0 0 0-2 2z"/><path d="M20 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2z"/></svg>';
    b.onclick = () => abrirManual();
    hdr.insertBefore(b, hdr.firstChild);
  }
})();

// ── 🔍 Lupa del manual (29-sep, pedido Contreras): busca por palabra, sin tildes ni mayúsculas.
//    Deja solo las secciones que la contienen, dentro de ellas los pasos que la contienen,
//    y resalta la palabra. Mismo bloque en todos los módulos (el de RRHH usa _mLupaFiltrar).
function _mLupaNorm(s){ return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
function _mLupaMarcar(el, q){
  const nodos = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) nodos.push(w.currentNode);
  nodos.forEach(n => {
    const t = n.nodeValue; let norm = '', mapa = [];
    for (let i = 0; i < t.length; i++){ const c = _mLupaNorm(t[i]); for (let k = 0; k < c.length; k++){ norm += c[k]; mapa.push(i); } }
    let desde = 0, pos, frag = null, ult = 0;
    while (q && (pos = norm.indexOf(q, desde)) >= 0){
      frag = frag || document.createDocumentFragment();
      const a = mapa[pos], b = mapa[pos + q.length - 1] + 1;
      if (a > ult) frag.appendChild(document.createTextNode(t.slice(ult, a)));
      const m = document.createElement('mark'); m.textContent = t.slice(a, b);
      m.style.cssText = 'background:#fde047;color:inherit;padding:0 1px;border-radius:3px'; frag.appendChild(m);
      ult = b; desde = pos + q.length;
    }
    if (frag){ if (ult < t.length) frag.appendChild(document.createTextNode(t.slice(ult))); n.parentNode.replaceChild(frag, n); }
  });
}
function _mLupaFiltrar(cont, selSec, texto, info){
  if (!cont) return;
  const q = _mLupaNorm(String(texto || '').trim());
  let vistas = 0;
  cont.querySelectorAll(selSec).forEach(sec => {
    if (sec.dataset.mOrig == null) sec.dataset.mOrig = sec.innerHTML; else sec.innerHTML = sec.dataset.mOrig;
    if (!q){ sec.style.display = ''; return; }
    const lis = [...sec.querySelectorAll('li')];
    const enLis = lis.filter(li => _mLupaNorm(li.textContent).includes(q));
    const hay = _mLupaNorm(sec.textContent).includes(q);
    sec.style.display = hay ? '' : 'none';
    if (!hay) return;
    vistas++;
    if (enLis.length) lis.forEach(li => { if (!enLis.includes(li)) li.style.display = 'none'; });
    _mLupaMarcar(sec, q);
  });
  if (info) info.textContent = !q ? '' : vistas ? `${vistas} ${vistas === 1 ? 'sección' : 'secciones'} con «${String(texto).trim()}»` : `No encontré «${String(texto).trim()}» en el manual.`;
  const primera = q && cont.querySelector('mark');
  if (primera) primera.scrollIntoView({block: 'center', behavior: 'smooth'});
}
function _manualLupa(ov){
  const head = ov && ov.querySelector('.m-head'); if (!head) return;
  head.style.flexWrap = 'wrap';
  const box = document.createElement('div');
  box.style.cssText = 'flex-basis:100%;display:flex;gap:8px;align-items:center;margin-top:8px';
  box.innerHTML = '<input type="search" placeholder="🔍 Buscar en el manual (por ej.: equivalencias, remito, echeq)…" '
    + 'style="flex:1;min-width:0;padding:8px 11px;border-radius:9px;border:none;font-size:14px;color:#0f172a;font-family:inherit">'
    + '<span class="m-lupa-info" style="font-size:12px;opacity:.9;white-space:nowrap"></span>';
  head.appendChild(box);
  const inp = box.querySelector('input'), info = box.querySelector('.m-lupa-info');
  let t = null;
  inp.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => _mLupaFiltrar(ov, '.m-sec', inp.value, info), 250); });
  inp.addEventListener('keydown', e => { if (e.key === 'Escape' && inp.value){ e.stopPropagation(); inp.value = ''; _mLupaFiltrar(ov, '.m-sec', '', info); } });
  setTimeout(() => inp.focus(), 50);
}
