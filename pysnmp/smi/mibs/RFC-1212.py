
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

mibBuilder.exportSymbols(
    'RFC-1212',
    MibIdentifier=MibIdentifier,
    MibVariable=MibVariable,
    MibTableColumn=MibTableColumn,
    MibTableRow=MibTableRow,
    MibTable=MibTable
    )
    
