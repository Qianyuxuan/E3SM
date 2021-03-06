MODULE shr_mem_mod

  use shr_kind_mod, only : shr_kind_r8
  use shr_log_mod, only: s_logunit => shr_log_Unit

  implicit none
  private

  ! PUBLIC: Public interfaces

  public ::  shr_mem_getusage, &
       shr_mem_init

  ! PUBLIC: Public interfaces

  real(shr_kind_r8) :: mb_blk = 0.0_shr_kind_r8

  !===============================================================================
CONTAINS
  !===============================================================================

  subroutine shr_mem_init(prt, strbuf)

    implicit none

    !----- arguments -----

    logical, optional :: prt
    character(len=*), optional :: strbuf
    !----- local -----

    ! --- Memory stats ---
    integer :: msize                   ! memory size (high water)
    integer :: mrss0,mrss1,mrss2       ! temporary rss
    integer :: mshare,mtext,mdatastack
    logical :: lprt
    integer :: ierr

    integer :: GPTLget_memusage

    real(shr_kind_r8),allocatable :: mem_tmp(:)

    !---------------------------------------------------

    lprt = .false.
    if (present(prt)) then
       lprt = prt
    endif

    ierr = GPTLget_memusage (msize, mrss0, mshare, mtext, mdatastack)
    allocate(mem_tmp(1024*1024*128))    ! 1 MWord, 1024 MB (128*8)
    mem_tmp = -1.0
    ierr = GPTLget_memusage (msize, mrss1, mshare, mtext, mdatastack)
    deallocate(mem_tmp)
    ierr = GPTLget_memusage (msize, mrss2, mshare, mtext, mdatastack)
    mb_blk = 0.0_shr_kind_r8
    if (mrss1 - mrss0 > 0) then
       mb_blk = (1024.0_shr_kind_r8)/((mrss1-mrss0)*1.0_shr_kind_r8)
    endif

    if (lprt) then
       write(s_logunit,'(A,f16.2)') '1 GB memory   alloc in MB is ',(mrss1-mrss0)*mb_blk
       write(s_logunit,'(A,f16.2)') '1 GB memory dealloc in MB is ',(mrss1-mrss2)*mb_blk
       write(s_logunit,'(A,f16.2)') 'Memory block size conversion in Kbytes is ',mb_blk*1024_shr_kind_r8
    endif
    if (present(strbuf)) then
       write(strbuf,'(3(A,f16.2))') '1 GB memory   alloc in MB is ',(mrss1-mrss0)*mb_blk, &
                                  '\n1 GB memory dealloc in MB is ',(mrss1-mrss2)*mb_blk, &
                                  '\nMemory block size conversion in Kbytes is ',mb_blk*1024_shr_kind_r8
    endif


  end subroutine shr_mem_init

  !===============================================================================

  subroutine shr_mem_getusage(r_msize,r_mrss,prt)

    implicit none

    !----- arguments ---
    real(shr_kind_r8) :: r_msize,r_mrss
    logical, optional :: prt

    !----- local ---
    integer :: msize,mrss
    integer :: mshare,mtext,mdatastack
    integer :: ierr
    integer :: GPTLget_memusage, GPTLprint_memusage

    !---------------------------------------------------

    ierr = GPTLget_memusage (msize, mrss, mshare, mtext, mdatastack)
    r_msize = msize / 1024_shr_kind_r8
    r_mrss  = mrss  / 1024_shr_kind_r8

    if (present(prt)) then
       if (prt) then
          ierr = GPTLprint_memusage(' ')
       endif
    endif


  end subroutine shr_mem_getusage

  !===============================================================================

END MODULE shr_mem_mod
