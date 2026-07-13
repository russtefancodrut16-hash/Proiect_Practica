Prezentare:  Tehnologii Anti-Cheat 

Slide 1: Introducere și Paradigma Client-Server
Titlu Prezentare: Tehnologii de tip Anti-cheat
Problema fundamentală: Într-un mediu de rețea, serverul ar trebui să dicteze regulile. Cu toate acestea, jocurile moderne necesită procesare masivă pe PC-ul clientului (Client-Side) pentru a evita lag-ul. 
Vulnerabilitatea: Deoarece datele jocului  se află fizic în memoria RAM a utilizatorului, un atacator cu acces la propriul hardware poate manipula aceste informații.

Slide 2: Arhitectura Inelelor de Protecție (CPU Protection Rings)
Pentru a înțelege cum funcționează un cheat, trebuie să explicăm cum procesorul (CPU) împarte privilegiile:
Ring 3 (User Space / Modul Utilizator): Aici rulează 99% din programe (Discord, Chrome, jocul în sine). Aplicațiile de aici nu au acces direct la hardware; trebuie să „ceară voie” sistemului de operare prin Apeluri de Sistem (Syscalls).
Ring 0 (Kernel Space / Modul Nucleu): Inima sistemului de operare. Aici rulează driverele plăcii video și managementul memoriei. Un cod executat în Ring 0 are acces absolut și neîngrădit oriunde în sistem.

Slide 3: Anatomia unui Cheat Clasic (Atacul din Ring 3)
Înainte de anti-cheat-urile kernel, cheat-ul opera direct din User Space, exploatând funcțiile Windows:
Memory Reading (Aimbot/Wallhack): Folosind API-ul `ReadProcessMemory()`, un cheat citește coordonatele 3D ale jucătorilor din memoria alocată jocului și le randează pe ecran.
DLL Injection: Trișorul injectează o bibliotecă `.dll` malițioasă în procesul jocului folosind `CreateRemoteThread()`.
Code Detouring: Odată injectat, codul malițios modifică instrucțiunile în limbaj de asamblare (Assembly) ale jocului 

Slide 4: Defensiva Supremă - Trecerea în Ring 0
Pentru a combate atacurile sofisticate, companiile au mutat securitatea tot în Ring 0.
Cum funcționează? Aceste programe sunt instalate ca Drivere de Windows (fișiere `.sys`).
Încărcare la Boot (Early-Launch Anti-Malware): Driverul se încarcă în memoria RAM imediat după pornirea Windows-ului, chiar înainte de pornirea multor servicii de sistem. Astfel, niciun cheat nu are timp să se ascundă înainte ca anti-cheat-ul să devină activ.

Slide 5: Tehnici de Detecție I - Interceptarea Apelurilor (Callbacks)
Un Anti-Cheat în Ring 0 nu mai scanează doar fișiere pe disc, ci blochează acțiunile direct în procesor:
Object Callbacks: Folosind funcția de kernel `ObRegisterCallbacks`, anti-cheat-ul spune Windows-ului: "Anunță-mă ori de câte ori un program încearcă să acceseze procesul jocului".
Blocarea Handle-urilor (Handle Stripping): Dacă un cheat încearcă să obțină un handle (o cheie de acces) cu drepturi de scriere în memoria jocului, driverul anti-cheat interceptează cererea și returnează eroarea `STATUS_ACCESS_DENIED`.

Slide 6: Tehnici de Detecție II - DKOM și Ascunderea Proceselor
Hackerii încearcă să își ascundă cheat-urile (care rulează și ele în Ring 0) manipulând structurile interne ale Windows-ului:
Direct Kernel Object Manipulation (DKOM): Hackerul șterge procesul cheat-ului din lista internă de procese a Windows-ului (`ActiveProcessLinks`). Task Manager-ul nu îl mai vede, deci pare invizibil.
Răspunsul Anti-Cheat-ului: Pentru a detecta un proces ascuns, anti-cheat-ul nu se mai uită în listele oficiale ale Windows-ului, ci scanează brut memoria RAM fizică sau interoghează direct thread-urile alocate de procesorul (CPU) la nivel de hardware.

Slide 7: Tehnici de Detecție III - Integritatea Paginării (Page Tables)
Atacul: Un cheat avansat poate modifica memoria fizică a jocului pe furiș.
Protecția (CR3 Register): Anti-Cheat-ul monitorizează tabelele de paginare (Page Tables), care fac traducerea dintre adresele de memorie virtuală și cele fizice. Verifică registrul `CR3` din procesor pentru a se asigura că nimeni nu a redirecționat memoria alocată jocului către un cod malițios.

Slide 8: Noul Câmp de Luptă - Atacurile Hardware (DMA)
Deoarece Ring 0 a devenit extrem de bine păzit, hackerii au renunțat complet la software și au trecut la hardware:
Direct Memory Access (DMA): Trișorul introduce în placa de bază un dispozitiv PCIe special (ex: PCIe Screamer, PCILeech). 
Cum ocolește sistemul? Dispozitivul DMA interacționează fizic direct cu plăcuțele de memorie RAM, citind curentul electric. Acesta ocolește complet procesorul (CPU) și sistemul de operare (OS). Driverul anti-cheat pur și simplu nu are cum să "vadă" hardware-ul citind memoria.

Slide 9: Soluția Hardware - TPM 2.0 și Secure Boot
Cum blochezi o componentă fizică invizibilă pentru sistemul de operare?
Cerințe obligatorii: Jocurile moderne  refuză să pornească dacă nu ai funcțiile Secure Boot și TPM 2.0 activate din BIOS.
IOMMU și HVCI: Anti-Cheat-urile se folosesc de Hypervisor-Protected Code Integrity. Această tehnologie folosește IOMMU (Input-Output Memory Management Unit) pentru a refuza accesul dispozitivelor PCIe neautorizate (cum sunt plăcile de cheat DMA) la memoria RAM a sistemului.

Slide 10: Controverse, Riscuri și Concluzii
Dilema de Securitate: Un anti-cheat la nivel de Kernel este arhitectural identic cu un Rootkit malițios. Are control deplin asupra camerei web, parolelor și fișierelor criptate.
Riscul Vulnerabilităților: Dacă un hacker din Rusia/China descoperă o vulnerabilitate  chiar în driverul Vanguard sau Easy Anti-Cheat, poate prelua controlul a zeci de milioane de calculatoare instantaneu, ocolind orice software antivirus existent.
Concluzie: În ciuda riscurilor de confidențialitate, tehnologia Ring 0 rămâne singura metodă reală, dovedită matematic și arhitectural, de a oferi o experiență de joc curată în mediul competitiv modern.
