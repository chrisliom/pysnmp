from pysnmp.proto import rfc1155

( MibIdentifier, 
  MibVariable,
  MibTableColumn,
  MibTableRow,
  MibTable ) = mibBuilder.importSymbols(   
    'SNMPv2-SMI',
    'MibIdentifier',
    'MibVariable',
    'MibTableColumn',
    'MibTableRow',
    'MibTable',
    )

iso = MibIdentifier((1,))
org = MibIdentifier((3,))
dod = MibIdentifier((6,))
internet = MibIdentifier(dod.name + (1,))
directory = MibIdentifier(internet.name + (1,))
mgmt = MibIdentifier(internet.name + (2,))
experimental = MibIdentifier(internet.name + (3,))
private = MibIdentifier(internet.name + (4,))
enterprises = MibIdentifier(private.name + (1,))

ObjectName = rfc1155.ObjectName

NetworkAddress = rfc1155.NetworkAddress
IpAddress = rfc1155.IpAddress
Counter = rfc1155.Counter
Gauge = rfc1155.Gauge
TimeTicks=rfc1155.TimeTicks
Opaque=rfc1155.Opaque

mibBuilder.exportSymbols(
    'RFC1155-SMI',
    iso=iso,
    org=org,
    dod=dod,
    internet=internet,
    directory=directory,
    mgmt=mgmt,
    experimental=experimental,
    private=private,
    enterprises=enterprises,
    MibIdentifier=MibIdentifier,
    MibVariable=MibVariable,
    MibTableColumn=MibTableColumn,
    MibTableRow=MibTableRow,
    MibTable=MibTable,
    ObjectName=ObjectName,
    NetworkAddress=NetworkAddress,
    IpAddress=IpAddress,
    Counter=Counter,
    Gauge=Gauge,
    TimeTicks=TimeTicks,
    Opaque=Opaque
    )
