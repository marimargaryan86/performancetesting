/* eslint-disable camelcase */
import type { LocaleData } from "$lib/i18n";

export default {
  title: "Junction Hub",
  roles: {
    "reseller-admin": "Administrador revendedor",
    "reseller-user": "Usuario revendedor",
    "snowfall-admin": "Administrador Snowfall",
    "snowfall-user": "Usuario Snowfall",
  },
  words: {
    yes: "Sí",
    no: "No",
    help: "Ayuda",
    unknown: "Desconocido",
    notAvailable: "N / A",
    subAccounts: "Subcuentas",
    balances: "Saldos",
    from: "Origen",
    to: "Destino",
    depart: "Fechas",
    passenger_one: "Pasajero",
    passenger_other: "Pasajeros",
    fareRules: "Reglas de tarifas",
    stop_zero: "Directo",
    stop_one: "Detener",
    stop_other: "Paradas",
    stopCounter_zero: "$t(words.stop_zero)",
    stopCounter: "{{count}} $t(words.stop, lowercase)",
    departureTime: "Hora de salida",
    departure: "Salida",
    arrival: "Llegada",
    journeyDuration: "Duración del viaje",
    railwayOperators: "Operadores ferroviarios",
    alternativeFares: "Tarifas disponibles",
    selected: "Seleccionado",
    dateRange: "Rango de fechas",
    none: "Ninguno",
    title: "Título",
    firstName: "Nombre",
    lastName: "Apellido",
    birthdayDate: "Fecha de Nacimiento",
    gender: "Género",
    documentType: "Tipo de Documento",
    documentNumber: "Número del Documento",
    expiryDate: "Fecha de caducidad",
    issueDate: "Fecha de emisión",
    issuingCountry: "País emisor",
    nationality: "Nacionalidad",
    residenceCountryCode: "Código de país de residencia",
    summary: "Resumen",
    fareBrand_one: "Tipo de tarifa",
    fareBrand_other: "Tipos de tarifas",
    itinerary: "Itinerario",
    fee_one: "Tarifa",
    fee_other: "Tarifas",
    serviceFee: "Tarifa de servicio",
    agencyMarkup: "Comision de agencia",
    paymentMethod: "Método de pago",
    contactInformation: "Información del contacto",
    countryCode: "Código de país",
    phoneNumber: "Número de teléfono",
    email: "Correo electrónico",
    addressLine1: "Dirección Línea 1",
    addressLine2: "Dirección Línea 2",
    city: "Ciudad",
    country: "País",
    postcode: "Código postal",
    error: "Error",
    success: "Éxito",
    warning: "Aviso",
    status: "Estado",
    passengerDetails: "Detalles del pasajero",
    itineraryDetails: "Detalles del itinerario",
    tripDuration: "Duración del viaje",
    orderReference: "Referencia de Pedido",
    cancellation: "Cancelación",
    reservationNumber: "Número de reserva",
    orderDetails: "Detalles del pedido",
    booking: "Reserva",
    bookingStatus: "Estado de la reservación",
    cancellationStatus: "Estado de cancelación",
    refund: "Reembolso",
    total: "Total",
    transactionInfo: "Información de la transacción",
    transactionType: "Tipo de transacción",
    paymentType: "Tipo de pago",
    provider: "Proveedor",
    reseller: "Revendedor",
    markup: "Margen",
    refundPosition: "Posición de reembolso",
    withoutAmounts: "Sin cantidades",
    withAmounts: "con cantidades",
    amount: "Cantidad",
    refundReference: "Referencia de reembolso",
    bookTrip: "Reservar un viaje",
    manageTrip: "Gestionar un viaje",
    passengerNameRecord: "Número de referencia",
    optional: "Opcional",
    inbound: "Entrante",
    outbound: "Saliente",
    admin: "Admin",
    user: "User",
    earlier: "Antes",
    later: "Después",
    ok: "Ok",
    profile: "Perfil",
    role: "Rol",
    resellers: "Revendedores",
    parentReseller: "Matriz",
    childReseller: "Filial",
  },
  actions: {
    logout: "Cerrar sesión",
    continue: "Continuar",
    cancel: "Cancelar",
    reportAnIssue: "Reportar un problema",
    click: "Hacer clic",
    goToLogin: "Ir a iniciar sesión",
    search: "Buscar",
    newOrder: "Nuevo orden",
    download: "Descargar",
    addBalance: "Agregar saldo",
    addBalances: "Agregar saldos",
    add: "Añadir",
    addDate: "añadir fecha",
    returnToBookings: "Volver a reservas",
    sortBy: "Ordenar por",
    selectAll: "Seleccionar todo",
    clearAll: "Limpiar todo",
    bookNow: "Reservar ahora",
    viewFareRules: "Ver reglas de tarifas",
    clear: "Limpiar",
    select: "Seleccionar",
    enterFirstName: "Introduzca el nombre",
    enterLastName: "Introduzca el apellido",
    enterDocumentNumber: "Introduzca el número de documento",
    enterIssuingCountry: "Introduzca el país emisor",
    enterNationality: "Introduzca la nacionalidad",
    enterResidenceCountryCode: "Introduzca el código del país de residencia",
    enterAmount: "Introduzca la cantidad",
    selectFeeType: "Seleccionar tipo de tarifa",
    tryAgain: "Intentar otra vez",
    enterPhoneNumber: "Introduzca número telefónico",
    enterEmail: "Introduzca correo electrónico",
    enterAddressLine1: "Introduzca la dirección en la línea 1",
    enterAddressLine2: "Introduzca la dirección en la línea 2",
    enterCity: "Introduce la ciudad",
    selectCountry: "Seleccionar país",
    enterPostcode: "Introduzca el código postal",
    next: "Siguiente",
    previous: "Regresar",
    book: "Crear Reserva",
    downloadTickets: "Descargar Tickets",
    cancelBooking: "Cancelar reserva",
    goBack: "Regresa",
    view: "Ver",
    cancelRequest: "Cancelar",
    refundWithNoAmount: "Reembolso sin importe",
    calculateRefundPosition: "Calcular la posición de reembolso",
    issueRefund: "Emitir Reembolso",
    enterRefundReference: "Introduzca la referencia de reembolso",
    bookTrip: "Reservar viaje",
    findTrip: "Buscar viaje",
    modifySearch: "Modificar búsqueda",
    addUser: "Agregar Usuario",
    save: "Ahorrar",
    change: "Cambiar",
    confirmSelection: "Confirmar selección",
    deactivate: "Desactivar",
    discard: "Descartar",
    enterUserDetails: "Introduzca los detalles de la cuenta del usuario",
    enterUserRole: "Definir el rol del usuario",
    resellersSearch: "Búsqueda de revendedores",
    deleteUser: "Borrar Usuario",
  },
  sentences: {
    priceChange: "Cambio de precio",
    priceChangeInfo:
      'Hemos notado un cambio de precio;  <strong typography="body-medium" weight="bold">{{originalPrice}}</strong>, y el nuevo precio es <strong typography="body-medium" weight="bold">{{newPrice}}</strong>. ',
    areYouSure: "¿Está seguro?",
    copiedToClipboard: "Copiado",
    noBalancesFound: "No se encontraron saldos",
    findABalance: "encontrar un saldo",
    cityOrStation: "Ciudad o Estación",
    noTripsMatchesTheFilterCriteria: "Ningún viaje coincide con los criterios del filtro",
    noTripsFound: "No se encontraron viajes",
    timeRemaining: "Tiempo restante",
    priceQuoteTimeRemainingInfo:
      '{{timeLeft}} minutos para <strong weight="bold">completar</strong> su reservación',
    offerSearchTimeRemainingInfo:
      '{{timeLeft}} minutos para <strong weight="bold">seleccionar</strong> su oferta',
    startingAt: "De",
    loadingTripDetails: "Cargando detalles del viaje...",
    thisPriceIsForAllPassengers: "Precio para todos pasajeros.",
    totalToPay: "Total a pagar",
    fareRulesInfo: [
      {
        type: "text",
        value:
          "Las tarifas no están garantizadas hasta que se reciba el pago completo y se emitan los boletos. ",
      },
      {
        type: "fareRulesButton",
        value: "Reglas de Tarifas",
      },
      {
        type: "text",
        value: "y",
      },
      {
        type: "fareRulesButton",
        value: "Reglas de Tarifas",
      },
    ],
    totalToCollect: "Total a cobrar",
    paymentDeclined: "Pago rechazado",
    anUnexpectedErrorOccurred: "Ocurrió un error inesperado",
    paymentInfo: [
      {
        type: "text",
        value: "Al reservar tu entrada aceptas las condiciones de Snowfall.",
      },
      {
        type: "toc",
        value: "t",
      },
      {
        type: "text",
        value: "el",
      },
      {
        type: "coc",
        value: "condiciones de transporte del transportista",
      },
      {
        type: "text",
        value: "y nuestro",
      },
      {
        type: "privacy",
        value: "política de privacidad",
      },
    ],
    oopsSomethingWentWrong: "Huy! Algo salió mal :(",
    theOrderWasCreatedSuccessfully: "El pedido fue creado exitosamente.",
    theOrderWasCreatedWithErrors: "El pedido fue creado con errores.",
    theOrderIsInAPendingState: "El pedido está en estado pendiente.",
    yourOrderHasBeenCreated: "Tu pedido ha sido creado",
    totalPaid: "Total pagado",
    newSearch: "Nueva búsqueda",
    youAreCancellingThisBooking: "Estás cancelando esta reserva",
    rulesAndFees: "Reglas y tarifas",
    pleaseReviewTheFollowingRules:
      "Revise las siguientes reglas antes de cancelar, incluidas las tarifas aplicables.",
    doYouWishToContinue: "¿Desea continuar?",
    thisCannotBeUndone: "Esto no se puede deshacer.",
    cancellationRequestReceived: "Solicitud de cancelación recibida",
    cancellationRequestFailed: "La solicitud de cancelación falló",
    cancellationRequestInfo: "Hemos recibido su solicitud de cancelación. ",
    contactSnowfallSupport: "Puede ponerse en contacto con el soporte de Snowfall en",
    transactionNotFound: "Transacción no encontrada",
    toUs: "Para nosotros",
    payerCurrency: "Moneda del pagador",
    toReseller: "al revendedor",
    createRefundWithoutAmounts: "Crear reembolso sin cantidad",
    resellerHowMuchWeGiveBack: "Revendedor: cuánto devolvemos",
    providerHowMuchWeGetBack: "Proveedor: cuánto recuperamos",
    refundReferenceInfo:
      "El reembolso debe gestionarse manualmente; hágalo e ingrese la referencia de reembolso arriba",
    bookTrip:
      "Busque, reserve y pague contenido multimodal de miles de proveedores y operadores, en una sola reserva.",
    manageTrip:
      "Recupere su viaje para cambiar o cancelar reservas, ver/imprimir itinerario y mucho más.",
    passengerNameRecordPlaceholder: "Por ejemplo: 9A2FDF56",
    passengerLastNamePlaceholder: "Como en la confirmación de su reserva.",
    passengerNameRecordError: "Su referencia es una secuencia de ocho letras y/o números.",
    noTripsFoundMessage:
      "Asegúrese de haber ingresado el número de referencia correcto.\nInténtelo de nuevo o comuníquese con el soporte",
    adminRoleDescription:
      "View and manage any orders made within the agency. Manage reseller & user settings.",
    userRoleDescription: "View and manage your own orders for a personalized experience.",
    totalAmount: "Cantidad total",
    fetchingSelection: "Obteniendo selección",
    previousSelectedOutboundUnavailable:
      "Tu viaje de ida seleccionado previamente ya no está disponible",
    previousSelectedInboundUnavailable:
      "Su viaje entrante seleccionado previamente ya no está disponible",
    deleteUser: "¿Estás seguro de que quieres desactivar a este usuario?",
    discardChangesTitle: "¿Descartar los cambios?",
    discardChangesBody:
      "Tienes cambios sin guardar. ¿Estás seguro de que quieres salir sin guardarlos?",
    userChangesSuccess: "Tus cambios se han guardado con éxito.",
    userCreatePending: "El usuario ha sido creado y está pendiente de aprobación.",
    userError: "Hubo un error al guardar tus cambios. Por favor, inténtalo de nuevo.",
    userDeleteSuccess: "El usuario ha sido borrado con éxito.",
    searchResellers: "Buscar y añadir o borrar revendedores del usuario",
    typeToSearch: "Escriba 3+ caracteres para buscar",
    deleteUserInfo: "Borrar esta cuenta removerá permanentemente al usuario del sistema.",
  },
  tableHeaders: {
    id: "IDENTIFICACIÓN",
    orderId: "Reserva ID",
    createdDate: "Fecha de creación",
    updatedDate: "Fecha actualizada",
    owedToUs: "Debido a Nosotros",
    reconciledQuestion: "¿Reconciliado?",
    orderReference: "Referencia",
    ticket: "Ticket",
    tickets: "Tickets",
    departureDate: "Fecha de salida",
    passengers: "Pasajeros",
    totalPrice: "Precio total",
    bookingStatus: "Estado de la reservación",
    cancellationStatus: "Estado de cancelación",
    refundStatus: "Estado del reembolso",
    transactionType: "Tipo de transacción",
    paymentType: "Tipo de pago",
    payer: "Pagador",
    beneficiary: "Beneficiario",
    whatWeOwe: "lo que debemos",
    salesProfit: "Beneficio de ventas",
    reference: "Referencia",
    settlement: "Asentamiento",
    from: "De",
    to: "A",
    quoteRate: "Tarifa de cotización",
    transactionRate: "Tarifa de transacción",
    fxDelta: "Delta de divisas",
    fxBuffer: "Búfer de efectos",
    status: "Estado",
    booking: "Reserva",
    origin: "Origen",
    destination: "Destino",
  },
  transportTypes: {
    rail: "Tren",
    car: "Alquiler de coches",
  },
  gender: {
    female: "Mujer",
    male: "Hombre",
    unspecified: "No especificado",
  },
  documentTypes: {
    passport: "Pasaporte",
  },
  passengerTitle: {
    miss: "Srta",
    mr: "Sr",
    mrs: "Sra",
    ms: "Srta",
    unspecified: "No especificado",
  },
  passengerTypes: {
    adult_one: "Adulto",
    adult_other: "Adultos",
    child_one: "Niño",
    child_other: "Niños",
    senior_one: "Persona Mayor",
    senior_other: "Personas Mayores",
    youth_one: "Jóven",
    youth_other: "Jóvenes",
  },
  tripTypes: {
    "round-trip": "Ida y vuelta",
    "one-way": "De una sola mano",
  },
  types: {
    "bank-transfer": "Transferencia bancaria",
    card: "Tarjeta",
    invoice: "Factura",
    transactional: "Transaccional",
    unspecified: "No especificado",
  },
  priceBreakdownTypes: {
    "base-fare": "Tarifa base",
    "company-mark-up": "margen de empresa",
    "reseller-mark-up": "Margen de revendedor",
    "service-mark-up": "margen de servicio",
    tax: "Impuestos",
  },
  sortOptions: {
    "earliest-arrival": "Llegada más temprana",
    "earliest-departure": "Salida más temprana",
    "lowest-price": "Precio más bajo",
    fastest: "Lo más rápido",
  },
  statuses: {
    active: "Active",
    confirmed: "Confirmado",
    "no-refund": "No hay reembolso",
    "not-ticketed": "No boletado",
    "refund-due": "Reembolso pendiente",
    "refund-failed": "Reembolso fallido",
    "refund-issued": "Reembolso emitido",
    cancelled: "Cancelado",
    completed: "Realizado",
    deleted: "Eliminado",
    error: "Error",
    executed: "Ejecutado",
    failed: "Fallido",
    mixed: "Mezclado",
    pending: "Pendiente",
    rejected: "Rechazado",
    submitted: "Enviado",
    succeeded: "Tuvo éxito",
    unknown: "Desconocido",
    unspecified: "No especificado",
  },
  pages: {
    dashboard: {
      title: "Panel",
      intro: "<strong>Bienvenido a</strong><span>Junction Hub</span>",
    },
    account: {
      title: "Configuraciones de la cuenta",
    },
    adminControls: {
      title: "Controles de Administrador",
      pages: {
        users: {
          title: "Usuarios",
          pages: {
            create: {
              title: "Agregar Usuario",
              subTitle: "Crear un nuevo usuario",
            },
            update: {
              title: "Actualizar Usuario",
              subTitle: "Actualizar la información del usuario",
            },
            delete: {
              title: "Eliminar Usuario",
              subTitle: "Eliminar un usuario",
            },
          },
        },
      },
    },
    help: {
      title: "Ayuda",
      pages: {
        privacyPolicy: {
          title: "Política de privacidad",
          content: `
<p>Creemos en proteger la privacidad del cliente final.</p>
<h2 typography="body-large" weight="bold">Indemnización</h2>
<p>Usted acepta defendernos a nosotros y/o a nuestros respectivos proveedores y a cualquiera de sus funcionarios, directores, empleados y agentes de y contra cualquier reclamo, causa de acción, demanda, recuperación, pérdida, daño, multa, penalización u otros costos o gastos.</p>
<ul>
  <li>- Su incumplimiento de este Acuerdo o de los documentos aquí mencionados;</li>
  <li>- Su violación de cualquier ley o de los derechos de un tercero; </li>
  <li>- Su uso del Booking Hub.</li>
</ul>
<h2 typography="body-large" weight="bold">Convertidor de moneda, precio y pago</h2>
<p>Los precios de los servicios de viajes son dinámicos y están sujetos a cambios frecuentes en cualquier momento.</p>
<p>Los precios mostrados a través de nuestro servicio pueden incluir impuestos.</p>
<p>En determinadas jurisdicciones, cuando corresponda, el cliente final también puede ser responsable de pagar los impuestos locales impuestos por las autoridades fiscales locales (como impuestos municipales o impuestos turísticos, etc.).</p>
<p>El importe de los impuestos locales puede cambiar entre la fecha de reserva y la fecha de estancia.</p>
<p>El pago se realiza directamente a Snowfall Limited en nombre del proveedor de viajes únicamente.</p>
<p>El proveedor de viajes suele exigir el pago por adelantado;</p>
<p>Podemos almacenar los detalles del método de pago del cliente final para transacciones futuras si ha obtenido su consentimiento para hacerlo.</p>
<p>Como se mencionó anteriormente, usted acepta las políticas aplicables tal como se muestran en el proceso de reserva.</p>
<p>Como realiza una reserva en nombre de otra persona, acepta la responsabilidad de obtener su permiso antes de proporcionarnos sus datos personales.</p>
<h2 typography="body-large" weight="bold">Cancelaciones y Reembolsos</h2>
<p>Los gastos de cancelación aplicados a la reserva están sujetos a la política específica establecida por el proveedor respectivo.</p>
<h2 typography="body-large" weight="bold">Terminación de cuenta</h2>
<p>A nuestro exclusivo criterio, podemos cancelar los titulares de cuentas que se consideren infractores reincidentes.</p>
<h2 typography="body-large" weight="bold">General</h2>
<p>Si se determina que alguna parte de este Acuerdo es inválida, ilegal o inaplicable, la validez, legalidad y aplicabilidad de las disposiciones restantes no se verán afectadas ni perjudicadas de ninguna manera.</p>
<p>El acceso a este Centro de reservas está condicionado a su aceptación de que toda la información contenida en él y todos los asuntos que surjan entre usted y nosotros se regirán por las leyes de Inglaterra y Gales.</p>
<p>Todos los derechos no otorgados expresamente en este documento están reservados.</p>
<h2 typography="body-large" weight="bold">Contacto</h2>
<p>Todos los comentarios, consultas y solicitudes relacionadas con nuestro uso de su información deben dirigirse a <a href="mailto:legal@snowfalltravel.com">legal@snowfalltravel.com</a></p>`,
        },
        termsAndConditions: {
          title: "Términos y condiciones",
          content: `
<h2 typography="body-large" weight="bold">Condiciones de uso de reserva</h2>
<p>Estos Términos de reserva (los "Términos") se aplican a las reservas realizadas a través del portal de clientes en línea de Junction (el "Centro de reservas"), que es propiedad y está operado por Snowfall Limited, una empresa registrada en Inglaterra (n.º de empresa: 12356236, 10-12 East</p>
<p>Lea atentamente el Acuerdo.</p>
<h2 typography="body-large" weight="bold">Condiciones de Uso</h2>
<p>Como condición para su uso del Booking Hub, Usted garantiza que (i) tiene al menos 18 años de edad;</p>
<h2 typography="body-large" weight="bold">Actividades prohibidas</h2>
<p>El contenido y la información del Booking Hub (incluidos, entre otros, el precio y la disponibilidad de los servicios de viaje), así como la infraestructura utilizada para proporcionar dicho contenido e información, son propiedad nuestra o de nuestros proveedores y proveedores.</p>
<h2 typography="body-large" weight="bold">Fraude</h2>
<p>Si una cuenta muestra signos repetidos de fraude, abuso, asociación con una persona o entidad sancionada por el gobierno u otra actividad sospechosa, podemos solicitarle información adicional.</p>
<p>Luego de revisar esa información y si llegamos a la conclusión razonable de que una reserva o cuenta está asociada con una actividad sospechosa, podremos:</p>
<ul>
  <li>- Cancelar cualquier reserva asociada con Su nombre, dirección de correo electrónico o cuenta;</li>
  <li>- Cerrar cualquier cuenta asociada;</li>
  <li>- Tomar acciones legales, incluso para buscar responsabilizarlo por cualquier pérdida.</li>
</ul>
<p>Comuníquese con nosotros sobre la cancelación de una reserva o el cierre de una cuenta si cree que se ha producido un error.</p>
<h2 typography="body-large" weight="bold">Hacer reservas de viajes</h2>
<p>Todos los servicios de viaje que pueda encontrar y/o reservar a través del Booking Hub son proporcionados por proveedores externos.</p>
<h2 typography="body-large" weight="bold">Limitaciones y exclusiones de responsabilidad</h2>
<p>Al operar Booking Hub, simplemente facilitamos reservas con terceros y no asumimos ninguna responsabilidad por proporcionar las opciones de viaje mostradas en Booking Hub o por cualquier acuerdo realizado con terceros en nombre del cliente final como resultado del uso de Booking Hub.</p>
<p>Nuestra máxima responsabilidad agregada hacia usted y/o el cliente final que surja de o en conexión con estos términos y condiciones o su acceso, uso o incapacidad de acceso o uso del Booking Hub se limitará al máximo permitido por</p>`,
        },
        customerService: {
          title: "Servicio al Cliente",
          content: `
<p>Contáctenos con su solicitud de asistencia especializada</p>
<p><a href="mailto:support@snowfalltravel.com?subject=GG%20-%20">soporte@snowfalltravel.com</a></p>`,
        },
        conditionsOfCarriage: {
          title: "Condiciones de Transporte",
          content: `
<p>Condiciones del operador del tren.</p>`,
        },
      },
    },
    knowledgeHub: {
      title: "Información de Apoyo",
      userManuals: {
        title: "Manuales de usuario",
        description:
          "Encuentre todo lo que necesita para acceder y comenzar a utilizar Junction Hub con nuestra útil guía del usuario.",
        userManual: "Junction Hub - Manual de usuario",
      },
      videos: {
        title: "Tutoriales en vídeo",
        description:
          "Conozca Junction Hub en solo unos minutos con nuestros rápidos tutoriales en vídeo.",
        items: [
          {
            title: "buscar un viaje",
            description: "Descubra cómo buscar viajes en tren en Junction Hub.",
            id: "qMTv6kNAIEU",
            lengthS: 60,
          },
          {
            title: "Seleccione una oferta",
            description:
              "Descubra cómo seleccionar una oferta para la reserva de su cliente en Junction Hub.",
            id: "JdfyhZU3kQg",
            lengthS: 69,
          },
          {
            title: "Agregar detalles del pasajero",
            description:
              "Descubra cómo agregar detalles de pasajeros a una reserva de tren en Junction Hub.",
            id: "Zcidy7py-xY",
            lengthS: 37,
          },
          {
            title: "Total a pagar, agregar comisión",
            description:
              "Descubra cómo ver los saldos de las reservas, las reglas de tarifas y agregar tarifas y comisiones.",
            id: "pB05rIT8N3I",
            lengthS: 63,
          },
          {
            title: "Confirmar una reserva",
            description:
              "Descubra cómo realizar un pago con su tarjeta de agencia y confirmar una reserva en Junction Hub.",
            id: "OQMqh6fCczo",
            lengthS: 69,
          },
          {
            title: "Comprobar el estado del pedido",
            description:
              "Descubra cómo ver todos sus pedidos existentes, verificar su estado y descargar los boletos de sus clientes en Junction Hub.",
            id: "2ZHcdPvcJ-U",
            lengthS: 47,
          },
        ],
      },
      faq: {
        title: "Preguntas frecuentes",
        items: [
          {
            question: "¿Qué operadores de trenes están disponibles a través de Junction Hub?",
            answer:
              "Junction Hub le brinda acceso a una gran cantidad de viajes en tren por toda Europa, a bordo de operadores como Eurostar, SNCF, Thalys, Deutsche Bahn y más.",
          },
          {
            question:
              "¿Puedo ver y comparar diferentes tiempos de viaje y precios en un solo lugar?",
            answer:
              "Al buscar en Junction Hub, podrá ver fácilmente todas las salidas disponibles para las fechas de viaje elegidas y comparar los diferentes tipos de tarifas y precios en nombre de sus clientes.",
          },
          {
            question: "¿Qué opciones de pago se aceptan?",
            answer:
              "Actualmente todos los pagos de reserva se realizan utilizando la tarjeta de crédito de su agencia.",
          },
          {
            question: "¿Cómo cancelo reservas en Junction Hub?",
            answer: "Para cancelar una reserva, deberá realizar una solicitud de cancelación. ",
          },
          {
            question: "¿Cómo accedo a los billetes de tren de los clientes?",
            answer:
              'Navegue a la pestaña "Pedidos", donde puede ver todos los pedidos existentes y su estado. ',
          },
          {
            question: "¿Cómo me comunico con atención al cliente?",
            answer:
              "El equipo de soporte de Snowfall está disponible para ayudarlo si tiene algún problema. ",
          },
        ],
      },
    },
    pay: {
      title: "Pagar",
      pages: {
        accounts: {
          title: "Cuentas",
        },
        activity: {
          title: "Actividad",
          pages: {
            transactions: {
              title: "Actas",
            },
            conversions: {
              title: "divisas",
            },
          },
        },
        bills: {
          title: "Facturas",
        },
      },
    },
    tripManagement: {
      title: "Gestión de viajes",
      pages: {
        book: {
          title: "Crear Reserva",
          pages: {
            rail: {
              pages: {
                search: {
                  title: "Buscar",
                  subTitle: "buscar ofertas",
                },
                select: {
                  title: "Seleccionar",
                  subTitle: "Seleccione una oferta",
                  outbound: 'Seleccionar <strong weight="bold">saliente</strong>',
                  inbound: 'Seleccionar <strong weight="bold">entrante</strong>',
                  findingOutbound: "Buscando ofertas salientes...",
                  findingInbound: "Buscando ofertas entrantes...",
                },
                payment: {
                  title: "Pagar",
                  subTitle: "Pagar",
                },
                confirmation: {
                  title: "Confirmación",
                  subTitle: "Confirmación",
                },
              },
            },
            car: {
              pages: {
                search: {
                  title: "Buscar",
                  subTitle: "buscar ofertas",
                },
                select: {
                  title: "Seleccionar",
                  subTitle: "Seleccione una oferta",
                },
                payment: {
                  title: "Pagar",
                  subTitle: "Pagar",
                },
                confirmation: {
                  title: "Confirmación",
                  subTitle: "Confirmación",
                },
              },
            },
          },
        },
        orders: {
          title: "Pedidos",
          pages: {
            bookings: {
              title: "Reservaciones",
            },
            details: {
              title: "Detalles",
            },
          },
        },
      },
    },
  },
  ory: {
    formGroups: {
      default: "Por defecto",
      password: "Actualiza contraseña",
      oidc: "OIDC",
      profile: "Perfil",
      link: "Enlace",
      code: "Código",
      totp: "Autenticación de dos factores",
      lookup_secret: "Códigos de recuperación de respaldo",
      webauthn: "Claves de seguridad",
    },
  },
} satisfies LocaleData;
