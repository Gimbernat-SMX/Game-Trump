# TASK: Reducir falsos positivos de antivirus en Windows

## Objetivo

Evitar que el `.exe` del juego sea marcado como malware por antivirus (especialmente Windows Defender), siguiendo buenas practicas de distribucion.

## Estado

Pendiente

## Checklist

- [ ] Revisar `game.spec` y build script para evitar empaquetado agresivo.
- [ ] Compilar sin UPX (`--noupx`) para reducir heuristicas sospechosas.
- [ ] Incluir metadatos claros del ejecutable (CompanyName, ProductName, FileVersion).
- [ ] Usar versionado consistente del binario (ejemplo: `1.0.0`).
- [ ] Firmar digitalmente el `.exe` con certificado de code signing.
- [ ] Añadir timestamp a la firma digital.
- [ ] Verificar el `.exe` en VirusTotal antes de publicar.
- [ ] Reportar falsos positivos a Microsoft Defender si aparecen.
- [ ] Publicar en canal confiable (GitHub Releases + checksum SHA256).
- [ ] Documentar para usuarios como verificar firma y hash.

## Notas tecnicas

- No existe garantia del 100%, pero firma digital + build limpio reduce mucho los bloqueos.
- Si se usa PyInstaller, evitar opciones de ofuscacion o compresion excesiva.

## Entregables futuros

- [ ] Script de build Windows reproducible.
- [ ] Script de firma (signtool) con timestamp.
- [ ] Guia de publicacion y verificacion para usuarios.
